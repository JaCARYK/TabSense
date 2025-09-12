let currentUser = null;
let currentSuggestions = null;
let selectedTabs = new Set();

document.addEventListener('DOMContentLoaded', function() {
    checkAuthState();
    setupEventListeners();
    
    // Initial dog entrance animation
    setTimeout(() => {
        const dogSprite = document.getElementById('dog-mascot');
        if (dogSprite) {
            dogSprite.style.animation = 'dog-entrance 0.5s ease-out';
        }
    }, 100);
});

function setupEventListeners() {
    // Auth events
    document.getElementById('show-signup').addEventListener('click', (e) => {
        e.preventDefault();
        showSignupForm();
    });

    document.getElementById('show-login').addEventListener('click', (e) => {
        e.preventDefault();
        showLoginForm();
    });

    document.getElementById('login-btn').addEventListener('click', handleLogin);
    document.getElementById('signup-btn').addEventListener('click', handleSignup);
    document.getElementById('logout-btn').addEventListener('click', handleLogout);

    // Action buttons
    document.getElementById('quick-clean').addEventListener('click', performQuickClean);
    document.getElementById('group-tabs').addEventListener('click', performAutoGroup);
    document.getElementById('close-duplicates').addEventListener('click', closeDuplicates);
    document.getElementById('select-all-close').addEventListener('click', selectAllToClose);
    document.getElementById('close-selected').addEventListener('click', closeSelectedTabs);
}

function showLoginForm() {
    document.getElementById('login-form').style.display = 'block';
    document.getElementById('signup-form').style.display = 'none';
}

function showSignupForm() {
    document.getElementById('signup-form').style.display = 'block';
    document.getElementById('login-form').style.display = 'none';
}

function showError(message) {
    const errorDiv = document.getElementById('error-message');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    setTimeout(() => {
        errorDiv.style.display = 'none';
    }, 5000);
}

function checkAuthState() {
    chrome.storage.local.get(['user'], function(result) {
        if (result.user) {
            currentUser = result.user;
            showMainInterface();
        } else {
            showAuthInterface();
        }
    });
}

// Add a ready check for the background script
function waitForBackgroundReady() {
    return new Promise((resolve) => {
        const checkReady = () => {
            chrome.runtime.sendMessage({ action: 'ping' }, function(response) {
                if (chrome.runtime.lastError || !response) {
                    setTimeout(checkReady, 500);
                } else {
                    resolve();
                }
            });
        };
        checkReady();
    });
}

async function handleLogin() {
    const email = document.getElementById('login-email').value.trim();
    const password = document.getElementById('login-password').value;

    if (!email || !password) {
        showError('Please enter both email and password');
        return;
    }

    chrome.runtime.sendMessage({
        action: 'login',
        email: email,
        password: password
    }, function(response) {
        if (response.success) {
            currentUser = { email: email };
            chrome.storage.local.set({ user: currentUser });
            showMainInterface();
        } else {
            showError(response.error || 'Login failed');
        }
    });
}

async function handleSignup() {
    const email = document.getElementById('signup-email').value.trim();
    const password = document.getElementById('signup-password').value;
    const confirmPassword = document.getElementById('signup-confirm-password').value;

    if (!email || !password || !confirmPassword) {
        showError('Please fill in all fields');
        return;
    }

    if (password !== confirmPassword) {
        showError('Passwords do not match');
        return;
    }

    chrome.runtime.sendMessage({
        action: 'signup',
        email: email,
        password: password
    }, function(response) {
        if (response.success) {
            currentUser = { email: email };
            chrome.storage.local.set({ user: currentUser });
            showMainInterface();
        } else {
            showError(response.error || 'Signup failed');
        }
    });
}

async function handleLogout() {
    chrome.runtime.sendMessage({ action: 'logout' }, function(response) {
        currentUser = null;
        chrome.storage.local.remove('user');
        showAuthInterface();
    });
}

function showAuthInterface() {
    document.getElementById('auth-container').style.display = 'block';
    document.getElementById('main-container').style.display = 'none';
    document.getElementById('loading').style.display = 'none';
}

function showMainInterface() {
    document.getElementById('auth-container').style.display = 'none';
    document.getElementById('main-container').style.display = 'block';
    document.getElementById('user-email').textContent = currentUser.email;
    
    // Initialize health score circle at 0 for animation
    const progressCircle = document.querySelector('.score-circle-progress');
    if (progressCircle) {
        progressCircle.style.strokeDashoffset = '226';
    }
    
    loadTabSuggestions();
}

function showLoading() {
    document.getElementById('loading').style.display = 'flex';
    document.getElementById('main-container').style.display = 'none';
}

function hideLoading() {
    document.getElementById('loading').style.display = 'none';
    document.getElementById('main-container').style.display = 'block';
}

async function loadTabSuggestions() {
    showLoading();
    
    // Wait for background script to be ready
    let retryCount = 0;
    const maxRetries = 5;
    
    const loadWithRetry = () => {
        return new Promise((resolve) => {
            // Get suggestions from background script
            chrome.runtime.sendMessage({ action: 'getSuggestions' }, function(response) {
                if (chrome.runtime.lastError || !response || !response.success) {
                    if (retryCount < maxRetries) {
                        retryCount++;
                        console.log(`Retrying... attempt ${retryCount}`);
                        setTimeout(() => {
                            loadWithRetry().then(resolve);
                        }, 1000 * retryCount); // Exponential backoff
                    } else {
                        resolve(null);
                    }
                } else {
                    resolve(response);
                }
            });
        });
    };
    
    const response = await loadWithRetry();
    
    if (response && response.success) {
        currentSuggestions = response.suggestions;
        const tabs = await chrome.tabs.query({});
        updateUI(tabs, response.suggestions);
        
        // Get tab stats
        chrome.runtime.sendMessage({ action: 'getTabStats' }, function(statsResponse) {
            if (statsResponse && statsResponse.success) {
                updateStats(statsResponse.stats);
            } else {
                // Fallback stats
                updateStats({
                    totalTabs: tabs.length,
                    unusedTabs: 0,
                    forgottenTabs: 0,
                    healthScore: 100
                });
            }
        });
    } else {
        showError('Extension is still initializing. Please try again in a moment.');
        
        // Show minimal fallback UI
        const tabs = await chrome.tabs.query({});
        updateStats({
            totalTabs: tabs.length,
            unusedTabs: 0,
            forgottenTabs: 0,
            healthScore: 100
        });
    }
    
    hideLoading();
}

function updateStats(stats) {
    document.getElementById('total-tabs').textContent = stats.totalTabs || 0;
    document.getElementById('can-close').textContent = 
        (stats.unusedTabs || 0) + (stats.forgottenTabs || 0);
    document.getElementById('forgotten').textContent = stats.forgottenTabs || 0;
    
    // Use health score from background script
    const healthScore = stats.healthScore !== undefined ? stats.healthScore : 100;
    updateHealthScore(healthScore);
}

function updateHealthScore(score) {
    const scoreElement = document.querySelector('.score-value');
    const progressCircle = document.querySelector('.score-circle-progress');
    const dogSprite = document.getElementById('dog-mascot');
    const speechBubble = document.getElementById('speech-bubble');
    const bubbleText = speechBubble.querySelector('.bubble-text');
    
    // Animate score counter
    animateScoreCounter(scoreElement, score);
    
    // Calculate circle progress (circumference = 2 * π * r = 2 * 3.14 * 36 ≈ 226)
    const circumference = 226;
    const offset = circumference - (score / 100 * circumference);
    
    // Set circle progress with animation
    progressCircle.style.strokeDashoffset = offset;
    
    // Update colors and dog state based on score
    let strokeColor, dogState, message;
    
    if (score >= 80) {
        strokeColor = '#28a745';
        dogState = 'happy';
        message = 'Nice job organizing your tabs!';
    } else if (score >= 60) {
        strokeColor = '#ffc107';
        dogState = 'neutral';
        message = 'Clean up your tabs please!';
    } else {
        strokeColor = '#dc3545';
        dogState = 'sad';
        message = 'I feel lost in this sea of tabs...';
    }
    
    // Apply color to progress circle
    progressCircle.style.stroke = strokeColor;
    
    // Update dog state
    dogSprite.className = 'dog-sprite ' + dogState;
    
    // Show speech bubble with message
    bubbleText.textContent = message;
    speechBubble.classList.add('show');
    
    // Hide speech bubble after 3 seconds
    setTimeout(() => {
        speechBubble.classList.remove('show');
    }, 3000);
}

function animateScoreCounter(element, targetScore) {
    const duration = 1000; // 1 second
    const startTime = Date.now();
    const startScore = parseInt(element.textContent) || 0;
    
    function updateCounter() {
        const elapsed = Date.now() - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Use easeOutCubic for smooth animation
        const easeProgress = 1 - Math.pow(1 - progress, 3);
        const currentScore = Math.round(startScore + (targetScore - startScore) * easeProgress);
        
        element.textContent = currentScore;
        
        if (progress < 1) {
            requestAnimationFrame(updateCounter);
        }
    }
    
    updateCounter();
}

function updateUI(tabs, suggestions) {
    // Update close suggestions
    const closeList = document.getElementById('close-list');
    closeList.innerHTML = '';
    
    if (suggestions.toClose && suggestions.toClose.length > 0) {
        document.getElementById('quick-clean-count').textContent = suggestions.toClose.length;
        
        suggestions.toClose.forEach(tab => {
            const tabElement = createTabElement(tab, 'close');
            closeList.appendChild(tabElement);
        });
        
        document.getElementById('close-section').style.display = 'block';
    } else {
        document.getElementById('close-section').style.display = 'none';
    }
    
    // Update forgotten tabs
    const forgottenList = document.getElementById('forgotten-list');
    forgottenList.innerHTML = '';
    
    if (suggestions.forgotten && suggestions.forgotten.length > 0) {
        suggestions.forgotten.forEach(tab => {
            const tabElement = createTabElement(tab, 'forgotten');
            forgottenList.appendChild(tabElement);
        });
        
        document.getElementById('forgotten-section').style.display = 'block';
    } else {
        document.getElementById('forgotten-section').style.display = 'none';
    }
    
    // Update duplicate count
    if (suggestions.duplicates && suggestions.duplicates.length > 0) {
        const duplicateCount = suggestions.duplicates.reduce((sum, dup) => {
            // Use closeTabs array if available (new format), otherwise calculate from tabs
            if (dup.closeTabs) {
                return sum + dup.closeTabs.length;
            } else if (dup.tabs) {
                return sum + dup.tabs.length - 1;
            }
            return sum;
        }, 0);
        document.getElementById('duplicate-count').textContent = duplicateCount;
        document.getElementById('duplicates').textContent = duplicateCount;
    } else {
        document.getElementById('duplicate-count').textContent = '0';
        document.getElementById('duplicates').textContent = '0';
    }
    
    // Update group suggestions
    const groupList = document.getElementById('group-list');
    groupList.innerHTML = '';
    
    // Handle both Map and plain object formats
    let groupCount = 0;
    if (suggestions.toGroup) {
        if (suggestions.toGroup instanceof Map) {
            // It's a Map
            groupCount = suggestions.toGroup.size;
            if (groupCount > 0) {
                suggestions.toGroup.forEach((tabs, domain) => {
                    const groupElement = createGroupElement(domain, tabs);
                    groupList.appendChild(groupElement);
                });
            }
        } else if (typeof suggestions.toGroup === 'object') {
            // Convert object to entries for compatibility
            const entries = Object.entries(suggestions.toGroup);
            groupCount = entries.length;
            entries.forEach(([domain, tabs]) => {
                const groupElement = createGroupElement(domain, tabs);
                groupList.appendChild(groupElement);
            });
        }
    }
    
    if (groupCount > 0) {
        document.getElementById('group-count').textContent = groupCount;
        document.getElementById('group-section').style.display = 'block';
    } else {
        document.getElementById('group-section').style.display = 'none';
        document.getElementById('group-count').textContent = '0';
    }
}

function createTabElement(tab, type) {
    const div = document.createElement('div');
    div.className = 'tab-item';
    div.dataset.tabId = tab.id;
    
    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.className = 'tab-checkbox';
    checkbox.addEventListener('change', (e) => {
        if (e.target.checked) {
            selectedTabs.add(tab.id);
            div.classList.add('selected');
        } else {
            selectedTabs.delete(tab.id);
            div.classList.remove('selected');
        }
        updateCloseButton();
    });
    
    const info = document.createElement('div');
    info.className = 'tab-info';
    
    const title = document.createElement('div');
    title.className = 'tab-title';
    title.textContent = tab.title || 'Untitled';
    
    const url = document.createElement('div');
    url.className = 'tab-url';
    url.textContent = tab.url || '';
    
    info.appendChild(title);
    info.appendChild(url);
    
    div.appendChild(checkbox);
    div.appendChild(info);
    
    if (type === 'close' && tab.reason) {
        const reason = document.createElement('div');
        reason.className = 'tab-reason';
        reason.textContent = tab.reason;
        div.appendChild(reason);
    }
    
    if (type === 'forgotten' && tab.daysAgo) {
        const days = document.createElement('div');
        days.className = 'tab-reason';
        days.textContent = `${tab.daysAgo} days ago`;
        div.appendChild(days);
    }
    
    return div;
}

function createGroupElement(domain, tabs) {
    const div = document.createElement('div');
    div.className = 'group-item';
    
    const header = document.createElement('div');
    header.className = 'group-header';
    
    const name = document.createElement('div');
    name.className = 'group-name';
    name.textContent = domain;
    
    const count = document.createElement('div');
    count.className = 'group-count';
    count.textContent = `${tabs.length} tabs`;
    
    header.appendChild(name);
    header.appendChild(count);
    
    const tabList = document.createElement('div');
    tabList.className = 'group-tabs';
    const titles = tabs.slice(0, 3).map(t => t.title).join(', ');
    tabList.textContent = titles + (tabs.length > 3 ? '...' : '');
    
    const button = document.createElement('button');
    button.className = 'group-btn';
    button.textContent = `Group ${tabs.length} tabs`;
    button.addEventListener('click', () => {
        const tabIds = tabs.map(t => t.id);
        chrome.runtime.sendMessage({
            action: 'groupTabs',
            tabIds: tabIds,
            groupName: domain
        }, function(response) {
            if (response.success) {
                loadTabSuggestions(); // Refresh
            }
        });
    });
    
    div.appendChild(header);
    div.appendChild(tabList);
    div.appendChild(button);
    
    return div;
}

function updateCloseButton() {
    const button = document.getElementById('close-selected');
    if (selectedTabs.size > 0) {
        button.style.display = 'block';
        button.textContent = `Close ${selectedTabs.size} Selected Tab${selectedTabs.size > 1 ? 's' : ''}`;
    } else {
        button.style.display = 'none';
    }
}

function selectAllToClose() {
    const checkboxes = document.querySelectorAll('#close-list .tab-checkbox');
    const allChecked = Array.from(checkboxes).every(cb => cb.checked);
    
    checkboxes.forEach(checkbox => {
        checkbox.checked = !allChecked;
        const tabItem = checkbox.closest('.tab-item');
        const tabId = parseInt(tabItem.dataset.tabId);
        
        if (!allChecked) {
            selectedTabs.add(tabId);
            tabItem.classList.add('selected');
        } else {
            selectedTabs.delete(tabId);
            tabItem.classList.remove('selected');
        }
    });
    
    updateCloseButton();
}

function closeSelectedTabs() {
    if (selectedTabs.size === 0) return;
    
    const tabIds = Array.from(selectedTabs);
    chrome.runtime.sendMessage({
        action: 'closeTabs',
        tabIds: tabIds
    }, function(response) {
        if (response.success) {
            selectedTabs.clear();
            loadTabSuggestions(); // Refresh
        }
    });
}

function performQuickClean() {
    if (!currentSuggestions || !currentSuggestions.toClose) return;
    
    const tabIds = currentSuggestions.toClose.map(t => t.id);
    if (tabIds.length === 0) return;
    
    if (confirm(`Close ${tabIds.length} suggested tabs?`)) {
        chrome.runtime.sendMessage({
            action: 'closeTabs',
            tabIds: tabIds
        }, function(response) {
            if (response.success) {
                loadTabSuggestions(); // Refresh
            }
        });
    }
}

function performAutoGroup() {
    if (!currentSuggestions || !currentSuggestions.toGroup) return;
    
    // Handle both object and Map formats
    let entries;
    if (currentSuggestions.toGroup instanceof Map) {
        if (currentSuggestions.toGroup.size === 0) return;
        entries = Array.from(currentSuggestions.toGroup.entries());
    } else {
        entries = Object.entries(currentSuggestions.toGroup);
        if (entries.length === 0) return;
    }
    
    entries.forEach(([domain, tabs]) => {
        const tabIds = tabs.map(t => t.id);
        chrome.runtime.sendMessage({
            action: 'groupTabs',
            tabIds: tabIds,
            groupName: domain
        });
    });
    
    setTimeout(() => loadTabSuggestions(), 1000); // Refresh after grouping
}

function closeDuplicates() {
    if (!currentSuggestions || !currentSuggestions.duplicates) return;
    
    const tabIds = [];
    currentSuggestions.duplicates.forEach(dup => {
        // Use closeTabs array if available (new format), otherwise use old format
        if (dup.closeTabs) {
            dup.closeTabs.forEach(tab => tabIds.push(tab.id));
        } else if (dup.tabs) {
            dup.tabs.slice(1).forEach(tab => tabIds.push(tab.id));
        }
    });
    
    if (tabIds.length === 0) return;
    
    if (confirm(`Close ${tabIds.length} duplicate tabs?`)) {
        chrome.runtime.sendMessage({
            action: 'closeTabs',
            tabIds: tabIds
        }, function(response) {
            if (response.success) {
                loadTabSuggestions(); // Refresh
            }
        });
    }
}