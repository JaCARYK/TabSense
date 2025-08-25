import { initializeApp } from './firebase-app.js';
import { getFirestore, collection, doc, setDoc, getDoc } from './firebase-firestore.js';
import { getAuth, signInWithEmailAndPassword, createUserWithEmailAndPassword, signOut } from './firebase-auth.js';

let firebaseApp = null;
let db = null;
let auth = null;
let currentUser = null;
const FLASK_API_URL = 'http://localhost:5000';

chrome.runtime.onInstalled.addListener(() => {
    console.log('TabSense extension installed');
    initializeFirebase();
});

function initializeFirebase() {
    const firebaseConfig = {
        apiKey: "YOUR_API_KEY",
        authDomain: "YOUR_AUTH_DOMAIN",
        projectId: "YOUR_PROJECT_ID",
        storageBucket: "YOUR_STORAGE_BUCKET",
        messagingSenderId: "YOUR_MESSAGING_SENDER_ID",
        appId: "YOUR_APP_ID"
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

chrome.tabs.onActivated.addListener(async (activeInfo) => {
    if (!currentUser) return;
    
    try {
        const tab = await chrome.tabs.get(activeInfo.tabId);
        if (tab.url && !isSystemPage(tab.url)) {
            trackTabVisit(tab.url);
        }
    } catch (error) {
        console.error('Error tracking tab activation:', error);
    }
});

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (!currentUser) return;
    
    if (changeInfo.status === 'complete' && tab.url && !isSystemPage(tab.url)) {
        trackTabVisit(tab.url);
    }
});

function isSystemPage(url) {
    return url.startsWith('chrome://') || 
           url.startsWith('chrome-extension://') || 
           url.startsWith('about:') ||
           url.startsWith('file://') ||
           url === 'chrome://newtab/';
}

async function trackTabVisit(url) {
    if (!currentUser || !db) return;

    try {
        const urlObj = new URL(url);
        const hostname = urlObj.hostname;
        const now = new Date();
        
        const timestamp = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')} ${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}`;
        
        const userDocRef = doc(db, 'Data', currentUser.email);
        const userDoc = await getDoc(userDocRef);
        
        let userData = {};
        if (userDoc.exists()) {
            userData = userDoc.data();
        }
        
        userData[timestamp] = hostname;
        
        await setDoc(userDocRef, userData);
        console.log('Tab visit tracked:', hostname, timestamp);
    } catch (error) {
        console.error('Error tracking tab visit:', error);
    }
}

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
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

    if (request.action === 'getPrediction') {
        fetch(request.url)
            .then(response => response.text())
            .then(prediction => {
                if (prediction === 'Not enough data to predict.') {
                    sendResponse({ success: false, error: 'Not enough data' });
                } else {
                    sendResponse({ success: true, prediction: prediction });
                }
            })
            .catch(error => sendResponse({ success: false, error: error.message }));
        return true;
    }

    if (request.action === 'getStats') {
        getStats(request.email)
            .then(stats => sendResponse({ success: true, ...stats }))
            .catch(error => sendResponse({ success: false, error: error.message }));
        return true;
    }
});

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
        
        const userDocRef = doc(db, 'Data', email);
        await setDoc(userDocRef, {});
        
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

async function getStats(email) {
    if (!db) return { totalUrls: 0, accuracy: null };

    try {
        const userDocRef = doc(db, 'Data', email);
        const userDoc = await getDoc(userDocRef);
        
        if (userDoc.exists()) {
            const data = userDoc.data();
            const totalUrls = Object.keys(data).length;
            
            return { totalUrls, accuracy: null };
        }
        
        return { totalUrls: 0, accuracy: null };
    } catch (error) {
        console.error('Error getting stats:', error);
        return { totalUrls: 0, accuracy: null };
    }
}

chrome.storage.local.get(['user'], function(result) {
    if (result.user) {
        currentUser = result.user;
    }
});