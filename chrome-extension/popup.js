let currentUser = null;
const FLASK_API_URL = 'http://localhost:5001';

document.addEventListener('DOMContentLoaded', function() {
    checkAuthState();
    setupEventListeners();
});

function setupEventListeners() {
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
    document.getElementById('refresh-prediction').addEventListener('click', getPrediction);

    document.getElementById('login-email').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleLogin();
    });

    document.getElementById('login-password').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleLogin();
    });
}

function showLoginForm() {
    document.getElementById('login-form').style.display = 'block';
    document.getElementById('signup-form').style.display = 'none';
    clearError();
}

function showSignupForm() {
    document.getElementById('signup-form').style.display = 'block';
    document.getElementById('login-form').style.display = 'none';
    clearError();
}

function showError(message) {
    const errorDiv = document.getElementById('error-message');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    setTimeout(() => {
        errorDiv.style.display = 'none';
    }, 5000);
}

function clearError() {
    document.getElementById('error-message').style.display = 'none';
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

async function handleLogin() {
    const email = document.getElementById('login-email').value.trim();
    const password = document.getElementById('login-password').value;

    if (!email || !password) {
        showError('Please enter both email and password');
        return;
    }

    try {
        chrome.runtime.sendMessage({
            action: 'login',
            email: email,
            password: password
        }, function(response) {
            if (response.success) {
                currentUser = { email: email };
                chrome.storage.local.set({ user: currentUser });
                showMainInterface();
                getPrediction();
            } else {
                showError(response.error || 'Login failed');
            }
        });
    } catch (error) {
        showError('Login error: ' + error.message);
    }
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

    if (password.length < 6) {
        showError('Password must be at least 6 characters');
        return;
    }

    try {
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
    } catch (error) {
        showError('Signup error: ' + error.message);
    }
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
    showLoginForm();
}

function showMainInterface() {
    document.getElementById('auth-container').style.display = 'none';
    document.getElementById('main-container').style.display = 'block';
    document.getElementById('user-email').textContent = currentUser.email;
    updateStats();
    getPrediction();
}

async function getPrediction() {
    if (!currentUser) return;

    showPredictionLoading();

    chrome.tabs.query({ active: true, currentWindow: true }, async function(tabs) {
        const currentTab = tabs[0];
        const currentUrl = new URL(currentTab.url).hostname;
        const now = new Date();

        const requestUrl = `${FLASK_API_URL}/predict/${now.getMonth() + 1}/${now.getDate()}/${now.getHours()}/${now.getMinutes()}/${encodeURIComponent(currentUrl)}/${currentUser.email}/`;

        try {
            chrome.runtime.sendMessage({
                action: 'getPrediction',
                url: requestUrl
            }, function(response) {
                if (response.success && response.prediction) {
                    showPredictionResult(response.prediction);
                } else if (response.error === 'Not enough data') {
                    showNoPrediction();
                } else {
                    showPredictionError();
                }
            });
        } catch (error) {
            console.error('Prediction error:', error);
            showPredictionError();
        }
    });
}

function showPredictionLoading() {
    document.getElementById('loading-prediction').style.display = 'block';
    document.getElementById('prediction-result').style.display = 'none';
    document.getElementById('no-prediction').style.display = 'none';
}

function showPredictionResult(url) {
    document.getElementById('loading-prediction').style.display = 'none';
    document.getElementById('prediction-result').style.display = 'block';
    document.getElementById('no-prediction').style.display = 'none';

    const fullUrl = url.startsWith('http') ? url : `https://${url}`;
    document.getElementById('predicted-url').href = fullUrl;
    document.getElementById('predicted-url-text').textContent = url;
}

function showNoPrediction() {
    document.getElementById('loading-prediction').style.display = 'none';
    document.getElementById('prediction-result').style.display = 'none';
    document.getElementById('no-prediction').style.display = 'block';
}

function showPredictionError() {
    showNoPrediction();
}

async function updateStats() {
    if (!currentUser) return;

    chrome.runtime.sendMessage({
        action: 'getStats',
        email: currentUser.email
    }, function(response) {
        if (response.success) {
            document.getElementById('total-urls').textContent = response.totalUrls || 0;
            document.getElementById('prediction-accuracy').textContent = 
                response.accuracy ? `${response.accuracy}%` : '--';
        }
    });
}