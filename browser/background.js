// Background service worker for Media Processor Chrome Extension

// Create context menu when extension is installed
chrome.runtime.onInstalled.addListener(() => {
    chrome.contextMenus.create({
        id: "sendToMediaProcessor",
        title: "Send to Media Processor",
        contexts: ["page", "link", "video", "audio"]
    });
});

// Handle context menu clicks
chrome.contextMenus.onClicked.addListener((info, tab) => {
    if (info.menuItemId === "sendToMediaProcessor") {
        let url = info.linkUrl || info.srcUrl || tab.url;
        sendToMediaProcessor(url);
    }
});

// Handle browser action clicks
chrome.action.onClicked.addListener((tab) => {
    sendToMediaProcessor(tab.url);
});

// Function to send URL to Media Processor
function sendToMediaProcessor(url) {
    if (!url) return;
    
    // Create the protocol URL
    const protocolUrl = `mediaprocessor://${encodeURIComponent(url)}`;
    
    // Try to open the protocol URL
    chrome.tabs.create({ url: protocolUrl }, (tab) => {
        // If the protocol handler isn't registered, the tab will show an error
        // We can detect this and show instructions
        setTimeout(() => {
            chrome.tabs.get(tab.id, (updatedTab) => {
                if (chrome.runtime.lastError) {
                    // Tab was closed, likely protocol handler worked
                    console.log('URL sent to Media Processor successfully');
                } else if (updatedTab.url.startsWith('chrome-error://')) {
                    // Protocol handler not registered
                    showSetupInstructions();
                    chrome.tabs.remove(tab.id);
                }
            });
        }, 1000);
    });
}

// Show setup instructions if protocol handler isn't registered
function showSetupInstructions() {
    chrome.tabs.create({
        url: chrome.runtime.getURL('setup.html')
    });
}

// Handle messages from content script or popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "sendUrl") {
        sendToMediaProcessor(request.url);
        sendResponse({ success: true });
    } else if (request.action === "getCurrentUrl") {
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            sendResponse({ url: tabs[0]?.url || '' });
        });
        return true; // Keep message channel open for async response
    }
});

// Badge management
function updateBadge(text, color = '#4285f4') {
    chrome.action.setBadgeText({ text: text });
    chrome.action.setBadgeBackgroundColor({ color: color });
}

// Clear badge after a delay
function clearBadge(delay = 3000) {
    setTimeout(() => {
        chrome.action.setBadgeText({ text: '' });
    }, delay);
}

// Update badge when URL is sent
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "urlSent") {
        updateBadge('✓', '#4caf50');
        clearBadge();
    }
});