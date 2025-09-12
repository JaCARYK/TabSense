import { initializeApp } from './firebase-app.js';
import { getFirestore, collection, doc, setDoc, getDoc, updateDoc } from './firebase-firestore.js';
import { getAuth, signInWithEmailAndPassword, createUserWithEmailAndPassword, signOut } from './firebase-auth.js';

let firebaseApp = null;
let db = null;
let auth = null;
let currentUser = null;
const FLASK_API_URL = 'http://localhost:5001';

// Tab tracking data structure
const tabData = new Map();
const TAB_CLEANUP_THRESHOLD = 7 * 24 * 60 * 60 * 1000; // 7 days in milliseconds
const FORGOTTEN_TAB_THRESHOLD = 3 * 24 * 60 * 60 * 1000; // 3 days
const INACTIVE_TAB_THRESHOLD = 60 * 60 * 1000; // 1 hour

// Track initialization state
let isInitialized = false;
let initializationPromise = null;

// Initialize when extension is installed
chrome.runtime.onInstalled.addListener(async () => {
    console.log('TabSense Declutter installed');
    await initializeExtension();
});

// Also reinitialize when extension starts (e.g., browser restart)
chrome.runtime.onStartup.addListener(async () => {
    console.log('TabSense Declutter starting up');
    await initializeExtension();
});

// Initialize when service worker starts
chrome.runtime.onSuspend.addListener(() => {
    console.log('Service worker suspending');
});

// Initialize immediately when service worker loads
initializeExtension().catch(error => {
    console.error('Failed to initialize on startup:', error);
});

async function initializeExtension() {
    // If already initialized or in progress, return the existing promise
    if (isInitialized) {
        return Promise.resolve();
    }
    
    if (initializationPromise) {
        return initializationPromise;
    }
    
    initializationPromise = (async () => {
        try {
            console.log('Starting extension initialization...');
            
            // Ensure Chrome APIs are ready
            await new Promise((resolve) => {
                if (chrome.runtime && chrome.tabs) {
                    resolve();
                } else {
                    setTimeout(resolve, 100);
                }
            });
            
            // Wait for Firebase to initialize
            await new Promise((resolve) => {
                initializeFirebase();
                setTimeout(resolve, 2000); // Increased timeout for Firebase
            });
            
            // Then initialize tab tracking with retry
            let retries = 3;
            while (retries > 0) {
                try {
                    await initializeTabTracking();
                    break;
                } catch (error) {
                    retries--;
                    if (retries === 0) throw error;
                    console.log(`Retrying tab initialization... ${retries} attempts left`);
                    await new Promise(resolve => setTimeout(resolve, 500));
                }
            }
            
            // Finally start periodic classification
            startPeriodicClassification();
            
            isInitialized = true;
            console.log('Extension fully initialized');
        } catch (error) {
            console.error('Extension initialization error:', error);
            // Reset so we can retry
            initializationPromise = null;
            isInitialized = false;
            throw error;
        }
    })();
    
    return initializationPromise;
}

function initializeFirebase() {
    const firebaseConfig = {
        apiKey: "AIzaSyDkAxvui00Uo_L3-1nugF8to_TG6Qu4uPI",
        authDomain: "tabsense-14916.firebaseapp.com",
        projectId: "tabsense-14916",
        storageBucket: "tabsense-14916.firebasestorage.app",
        messagingSenderId: "853012985837",
        appId: "1:853012985837:web:3400cff5c36788a843d9e4",
        measurementId: "G-4NPLFJ1JVF"
    };

    try {
        firebaseApp = initializeApp(firebaseConfig);
        db = getFirestore(firebaseApp);
        auth = getAuth(firebaseApp);
        console.log('Firebase initialized successfully');
    } catch (error) {
        console.error('Firebase initialization error:', error);
    }
}

// Initialize tab tracking for all existing tabs
async function initializeTabTracking() {
    const tabs = await chrome.tabs.query({});
    const now = Date.now();
    
    // Get recently visited URLs from history to estimate tab age
    const recentHistory = await chrome.history.search({
        text: '',
        startTime: now - (30 * 24 * 60 * 60 * 1000), // Last 30 days
        maxResults: 1000
    }).catch(() => []);
    
    const urlVisits = new Map();
    for (const item of recentHistory) {
        if (item.lastVisitTime) {
            urlVisits.set(item.url, item.lastVisitTime);
        }
    }
    
    tabs.forEach(tab => {
        // Estimate when tab was created based on history
        const lastVisit = urlVisits.get(tab.url) || now;
        const estimatedAge = now - lastVisit;
        
        // For existing tabs, assume some baseline activity
        // Active tab gets higher counts, others get moderate counts
        const baseActivationCount = tab.active ? 5 : 
                                   tab.pinned ? 10 : 
                                   estimatedAge < INACTIVE_TAB_THRESHOLD ? 2 : 1;
        
        const baseActiveTime = tab.active ? 30000 : 
                              tab.pinned ? 60000 :
                              estimatedAge < INACTIVE_TAB_THRESHOLD ? 10000 : 0;
        
        const data = {
            id: tab.id,
            url: tab.url,
            title: tab.title,
            domain: extractDomain(tab.url),
            createdAt: lastVisit, // Use estimated creation time
            lastActivated: tab.active ? now : (lastVisit + estimatedAge / 2),
            lastInteraction: tab.active ? now : lastVisit,
            activationCount: baseActivationCount,
            totalActiveTime: baseActiveTime,
            scrollEvents: 0,
            clickEvents: 0,
            isActive: tab.active,
            isPinned: tab.pinned,
            groupId: tab.groupId || -1,
            status: 'normal' // Will be classified after
        };
        
        // Now classify with proper data
        data.status = classifyTabStatus(tab, data);
        tabData.set(tab.id, data);
    });
    
    console.log(`Initialized tracking for ${tabs.length} existing tabs`);
}

// Extract base domain for grouping (handles subdomains)
function extractDomain(url) {
    if (!url) return '';
    try {
        const hostname = new URL(url).hostname;
        // Extract base domain (e.g., github.com from docs.github.com)
        const parts = hostname.split('.');
        if (parts.length > 2) {
            // Check for common two-part TLDs
            const twoPartTlds = ['co.uk', 'co.jp', 'co.in', 'com.au', 'com.br'];
            const lastTwo = parts.slice(-2).join('.');
            if (twoPartTlds.includes(lastTwo)) {
                return parts.slice(-3).join('.');
            }
            return parts.slice(-2).join('.');
        }
        return hostname;
    } catch {
        return '';
    }
}

// Periodically reclassify tabs based on their activity
function startPeriodicClassification() {
    // Run every 5 minutes
    setInterval(async () => {
        const tabs = await chrome.tabs.query({});
        tabs.forEach(tab => {
            const data = tabData.get(tab.id);
            if (data) {
                const oldStatus = data.status;
                data.status = classifyTabStatus(tab, data);
                if (oldStatus !== data.status) {
                    console.log(`Tab ${tab.id} status changed from ${oldStatus} to ${data.status}`);
                }
            }
        });
    }, 5 * 60 * 1000); // 5 minutes
}

// Classify tab status based on activity
function classifyTabStatus(tab, activity = {}) {
    const now = Date.now();
    const data = activity || tabData.get(tab.id) || {};
    
    // Pinned tabs are always kept
    if (tab.pinned) return 'pinned';
    
    // Check if tab is forgotten (not used in 3+ days)
    if (data.lastActivated && (now - data.lastActivated) > FORGOTTEN_TAB_THRESHOLD) {
        return 'forgotten';
    }
    
    // Check if tab was never really used (created but never activated)
    if (data.activationCount === 0 && data.createdAt && (now - data.createdAt) > INACTIVE_TAB_THRESHOLD) {
        return 'unused';
    }
    
    // Check if tab is barely used (low activity and old)
    const ageInHours = data.createdAt ? (now - data.createdAt) / (60 * 60 * 1000) : 0;
    if (ageInHours > 2 && data.totalActiveTime < 5000 && data.activationCount < 2) {
        return 'candidate_close';
    }
    
    // Frequently used tabs
    if (data.activationCount > 10 || data.totalActiveTime > 300000) { // 5+ minutes active
        return 'frequently_used';
    }
    
    return 'normal';
}

// Track tab activation
chrome.tabs.onActivated.addListener(async (activeInfo) => {
    const tab = await chrome.tabs.get(activeInfo.tabId);
    const data = tabData.get(tab.id) || createTabData(tab);
    
    // Update previous active tab's total time
    tabData.forEach((tabInfo, tabId) => {
        if (tabInfo.isActive && tabId !== tab.id) {
            tabInfo.totalActiveTime += Date.now() - tabInfo.lastActivated;
            tabInfo.isActive = false;
        }
    });
    
    data.lastActivated = Date.now();
    data.activationCount++;
    data.isActive = true;
    data.status = classifyTabStatus(tab, data);
    
    tabData.set(tab.id, data);
    trackTabActivity(tab.id, 'activated', data);
});

// Track new tabs
chrome.tabs.onCreated.addListener((tab) => {
    const data = createTabData(tab);
    tabData.set(tab.id, data);
    trackTabActivity(tab.id, 'created', data);
});

// Track tab updates
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete') {
        const data = tabData.get(tabId) || createTabData(tab);
        data.url = tab.url;
        data.title = tab.title;
        data.domain = extractDomain(tab.url);
        data.status = classifyTabStatus(tab, data);
        
        tabData.set(tabId, data);
        trackTabActivity(tabId, 'updated', data);
    }
});

// Track tab removal
chrome.tabs.onRemoved.addListener((tabId) => {
    const data = tabData.get(tabId);
    if (data) {
        trackTabActivity(tabId, 'closed', data);
        tabData.delete(tabId);
    }
});

// Create initial tab data structure
function createTabData(tab) {
    const now = Date.now();
    return {
        id: tab.id,
        url: tab.url,
        title: tab.title,
        domain: extractDomain(tab.url),
        createdAt: now,
        lastActivated: tab.active ? now : now - 60000, // If not active, assume it's been idle for 1 minute
        lastInteraction: now,
        activationCount: tab.active ? 1 : 0,
        totalActiveTime: 0,
        scrollEvents: 0,
        clickEvents: 0,
        isActive: tab.active,
        isPinned: tab.pinned,
        groupId: tab.groupId || -1,
        status: 'normal'
    };
}

// Track tab activity to Firebase
async function trackTabActivity(tabId, action, data) {
    if (!currentUser || !db) return;
    
    try {
        const timestamp = new Date().toISOString();
        const userDocRef = doc(db, 'TabActivity', currentUser.email);
        const activity = {
            tabId,
            action,
            timestamp,
            ...data
        };
        
        // Check if document exists, create if it doesn't
        const docSnap = await getDoc(userDocRef);
        if (!docSnap.exists()) {
            await setDoc(userDocRef, {
                tabs: { [tabId]: data },
                activity: { [timestamp]: activity }
            });
        } else {
            await updateDoc(userDocRef, {
                [`tabs.${tabId}`]: data,
                [`activity.${timestamp}`]: activity
            });
        }
    } catch (error) {
        console.error('Error tracking tab activity:', error);
    }
}

// Get tab suggestions for decluttering
async function getTabSuggestions() {
    const suggestions = {
        toClose: [],
        toGroup: new Map(),
        forgotten: [],
        duplicates: []
    };
    
    const tabs = await chrome.tabs.query({});
    const domains = new Map();
    
    tabs.forEach(tab => {
        const data = tabData.get(tab.id);
        if (!data) return;
        
        // Identify tabs to close (exclude pinned and grouped tabs)
        if ((data.status === 'candidate_close' || data.status === 'unused') && 
            !tab.pinned && (!tab.groupId || tab.groupId === -1)) {
            suggestions.toClose.push({
                id: tab.id,
                title: tab.title,
                url: tab.url,
                reason: data.status === 'unused' ? 'Never used' : 'Rarely used',
                confidence: data.activationCount === 0 ? 0.9 : 0.7
            });
        }
        
        // Identify forgotten tabs
        if (data.status === 'forgotten' && !tab.pinned) {
            suggestions.forgotten.push({
                id: tab.id,
                title: tab.title,
                url: tab.url,
                lastSeen: data.lastActivated,
                daysAgo: Math.floor((Date.now() - data.lastActivated) / (24 * 60 * 60 * 1000))
            });
        }
        
        // Group tabs by domain (only ungrouped tabs)
        if (data.domain && (!tab.groupId || tab.groupId === -1) && !tab.pinned) {
            if (!domains.has(data.domain)) {
                domains.set(data.domain, []);
            }
            domains.get(data.domain).push(tab);
        }
    });
    
    // Identify tabs to group (need at least 2 tabs for grouping)
    console.log('Domain grouping analysis:', Array.from(domains.entries()).map(([domain, tabs]) => 
        `${domain}: ${tabs.length} tabs`));
    
    domains.forEach((tabs, domain) => {
        if (tabs.length >= 2 && domain && domain !== '' && domain !== 'newtab') {
            // Only suggest grouping if tabs aren't already grouped together
            const groupIds = new Set(tabs.map(t => t.groupId).filter(id => id && id !== -1));
            if (groupIds.size <= 1) { // Not in groups or all in same group
                suggestions.toGroup.set(domain, tabs.map(t => ({
                    id: t.id,
                    title: t.title,
                    url: t.url
                })));
                console.log(`Suggesting group for ${domain} with ${tabs.length} tabs`);
            }
        }
    });
    
    // Find duplicate tabs (show which one to keep)
    const urlMap = new Map();
    tabs.forEach(tab => {
        if (!tab.url || tab.url === 'chrome://newtab/') return;
        if (!urlMap.has(tab.url)) {
            urlMap.set(tab.url, []);
        }
        urlMap.get(tab.url).push(tab);
    });
    
    urlMap.forEach((tabs, url) => {
        if (tabs.length > 1) {
            // Sort by activity to keep the most active one
            const sortedTabs = tabs.sort((a, b) => {
                const dataA = tabData.get(a.id);
                const dataB = tabData.get(b.id);
                if (!dataA || !dataB) return 0;
                // Prioritize: pinned > active > higher activation count > more recent
                if (a.pinned !== b.pinned) return a.pinned ? -1 : 1;
                if (a.active !== b.active) return a.active ? -1 : 1;
                if (dataA.activationCount !== dataB.activationCount) 
                    return dataB.activationCount - dataA.activationCount;
                return dataB.lastActivated - dataA.lastActivated;
            });
            
            suggestions.duplicates.push({
                url,
                count: tabs.length,
                keepTab: { id: sortedTabs[0].id, title: sortedTabs[0].title },
                closeTabs: sortedTabs.slice(1).map(t => ({ id: t.id, title: t.title }))
            });
        }
    });
    
    return suggestions;
}

// Message handlers
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'ping') {
        // Ensure we're initialized before saying we're ready
        initializeExtension()
            .then(() => sendResponse({ ready: true }))
            .catch(() => sendResponse({ ready: false }));
        return true;
    }

    if (request.action === 'login') {
        handleLogin(request.email, request.password)
            .then(result => sendResponse(result))
            .catch(error => sendResponse({ success: false, error: error.message }));
        return true;
    }

    if (request.action === 'signup') {
        handleSignup(request.email, request.password)
            .then(result => sendResponse(result))
            .catch(error => sendResponse({ success: false, error: error.message }));
        return true;
    }

    if (request.action === 'logout') {
        handleLogout()
            .then(result => sendResponse(result))
            .catch(error => sendResponse({ success: false, error: error.message }));
        return true;
    }

    if (request.action === 'getSuggestions') {
        // Ensure initialization before getting suggestions
        initializeExtension()
            .then(() => getTabSuggestions())
            .then(suggestions => {
                // Convert Map to object for serialization
                const serializedSuggestions = {
                    ...suggestions,
                    toGroup: suggestions.toGroup instanceof Map ? 
                        Object.fromEntries(suggestions.toGroup) : 
                        suggestions.toGroup
                };
                sendResponse({ success: true, suggestions: serializedSuggestions });
            })
            .catch(error => sendResponse({ success: false, error: error.message }));
        return true;
    }

    if (request.action === 'closeTabs') {
        chrome.tabs.remove(request.tabIds)
            .then(() => sendResponse({ success: true }))
            .catch(error => sendResponse({ success: false, error: error.message }));
        return true;
    }

    if (request.action === 'groupTabs') {
        chrome.tabs.group({ tabIds: request.tabIds })
            .then(groupId => {
                chrome.tabGroups.update(groupId, { 
                    title: request.groupName || 'Group',
                    color: request.color || 'blue'
                });
                sendResponse({ success: true, groupId });
            })
            .catch(error => sendResponse({ success: false, error: error.message }));
        return true;
    }

    if (request.action === 'getTabStats') {
        // Ensure initialization before getting stats
        initializeExtension()
            .then(async () => {
                // Get current tabs if tabData is empty
                if (tabData.size === 0) {
                    await initializeTabTracking();
                }
                
                const tabValues = Array.from(tabData.values());
                const stats = {
                    totalTabs: tabData.size,
                    activeTabs: tabValues.filter(t => t.isActive).length,
                    pinnedTabs: tabValues.filter(t => t.isPinned).length,
                    forgottenTabs: tabValues.filter(t => t.status === 'forgotten').length,
                    unusedTabs: tabValues.filter(t => t.status === 'unused' || t.status === 'candidate_close').length,
                    frequentlyUsed: tabValues.filter(t => t.status === 'frequently_used').length
                };
                
                // Calculate health score
                let healthScore = 100;
                
                // Deduct for too many tabs
                if (stats.totalTabs > 20) {
                    healthScore -= Math.min(30, (stats.totalTabs - 20) * 1.5);
                }
                
                // Deduct for unused/forgotten tabs
                const wastedTabs = stats.forgottenTabs + stats.unusedTabs;
                if (wastedTabs > 0) {
                    healthScore -= Math.min(40, wastedTabs * 5);
                }
                
                // Bonus for organization (pinned tabs, groups)
                const groupedTabs = tabValues.filter(t => t.groupId && t.groupId !== -1).length;
                if (stats.pinnedTabs > 0 || groupedTabs > 0) {
                    healthScore += Math.min(10, (stats.pinnedTabs + groupedTabs) * 2);
                }
                
                stats.healthScore = Math.max(0, Math.min(100, Math.round(healthScore)));
                
                sendResponse({ success: true, stats });
            })
            .catch(error => {
                console.error('Error getting tab stats:', error);
                sendResponse({ success: false, error: error.message });
            });
        return true;
    }
});

// Authentication handlers
async function handleLogin(email, password) {
    if (!auth) {
        await initializeFirebase();
    }

    try {
        const userCredential = await signInWithEmailAndPassword(auth, email, password);
        currentUser = userCredential.user;
        chrome.storage.local.set({ user: { email: currentUser.email } });
        return { success: true };
    } catch (error) {
        console.error('Login error:', error);
        return { success: false, error: error.message };
    }
}

async function handleSignup(email, password) {
    if (!auth) {
        await initializeFirebase();
    }

    try {
        const userCredential = await createUserWithEmailAndPassword(auth, email, password);
        currentUser = userCredential.user;
        chrome.storage.local.set({ user: { email: currentUser.email } });
        
        const userDocRef = doc(db, 'TabActivity', email);
        await setDoc(userDocRef, { tabs: {}, activity: {} });
        
        return { success: true };
    } catch (error) {
        console.error('Signup error:', error);
        return { success: false, error: error.message };
    }
}

async function handleLogout() {
    try {
        if (auth) {
            await signOut(auth);
        }
        currentUser = null;
        chrome.storage.local.remove('user');
        return { success: true };
    } catch (error) {
        console.error('Logout error:', error);
        return { success: false, error: error.message };
    }
}

// Check for existing user on startup
chrome.storage.local.get(['user'], function(result) {
    if (result.user) {
        currentUser = result.user;
    }
});