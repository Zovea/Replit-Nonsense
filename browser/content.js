// Content script for Media Processor Chrome Extension

// Check if we're on a media-rich page
function isMediaPage() {
    // Check for common media elements
    const hasVideo = document.querySelector('video, iframe[src*="youtube"], iframe[src*="vimeo"], iframe[src*="twitch"]');
    const hasAudio = document.querySelector('audio');
    const hasMediaLinks = document.querySelector('a[href*="youtube.com"], a[href*="vimeo.com"], a[href*="soundcloud.com"]');
    
    // Check URL patterns
    const url = window.location.href;
    const mediaPatterns = [
        /youtube\.com/,
        /youtu\.be/,
        /vimeo\.com/,
        /soundcloud\.com/,
        /twitch\.tv/,
        /dailymotion\.com/,
        /facebook\.com.*\/videos/,
        /instagram\.com.*\/p\//,
        /tiktok\.com/,
        /twitter\.com.*\/status/,
        /x\.com.*\/status/
    ];
    
    const isMediaUrl = mediaPatterns.some(pattern => pattern.test(url));
    
    return !!(hasVideo || hasAudio || hasMediaLinks || isMediaUrl);
}

// Add visual indicator for media pages
function addMediaIndicator() {
    if (!isMediaPage()) return;
    
    // Create a small indicator
    const indicator = document.createElement('div');
    indicator.id = 'media-processor-indicator';
    indicator.innerHTML = '🎬';
    indicator.title = 'Send to Media Processor (Right-click for menu)';
    indicator.style.cssText = `
        position: fixed;
        top: 10px;
        right: 10px;
        width: 40px;
        height: 40px;
        background: #4285f4;
        color: white;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 16px;
        cursor: pointer;
        z-index: 10000;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        transition: all 0.3s ease;
        opacity: 0.8;
    `;
    
    // Hover effects
    indicator.addEventListener('mouseenter', () => {
        indicator.style.opacity = '1';
        indicator.style.transform = 'scale(1.1)';
    });
    
    indicator.addEventListener('mouseleave', () => {
        indicator.style.opacity = '0.8';
        indicator.style.transform = 'scale(1)';
    });
    
    // Click handler
    indicator.addEventListener('click', () => {
        sendCurrentPageToMediaProcessor();
    });
    
    document.body.appendChild(indicator);
}

// Send current page to Media Processor
function sendCurrentPageToMediaProcessor() {
    const url = window.location.href;
    
    chrome.runtime.sendMessage({
        action: 'sendUrl',
        url: url
    }, (response) => {
        if (response && response.success) {
            showNotification('URL sent to Media Processor!', 'success');
        } else {
            showNotification('Failed to send URL. Make sure Media Processor is running.', 'error');
        }
    });
}

// Show notification
function showNotification(message, type = 'info') {
    // Remove existing notification
    const existing = document.getElementById('media-processor-notification');
    if (existing) {
        existing.remove();
    }
    
    const notification = document.createElement('div');
    notification.id = 'media-processor-notification';
    notification.textContent = message;
    
    const colors = {
        success: { bg: '#4caf50', text: 'white' },
        error: { bg: '#f44336', text: 'white' },
        info: { bg: '#2196f3', text: 'white' }
    };
    
    const color = colors[type] || colors.info;
    
    notification.style.cssText = `
        position: fixed;
        top: 60px;
        right: 10px;
        background: ${color.bg};
        color: ${color.text};
        padding: 12px 16px;
        border-radius: 4px;
        font-size: 14px;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        z-index: 10001;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        max-width: 300px;
        word-wrap: break-word;
        animation: slideIn 0.3s ease;
    `;
    
    // Add animation keyframes
    if (!document.getElementById('media-processor-styles')) {
        const style = document.createElement('style');
        style.id = 'media-processor-styles';
        style.textContent = `
            @keyframes slideIn {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
        `;
        document.head.appendChild(style);
    }
    
    document.body.appendChild(notification);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 3000);
}

// Listen for messages from background script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'sendCurrentPage') {
        sendCurrentPageToMediaProcessor();
        sendResponse({ success: true });
    }
});

// Initialize when page loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', addMediaIndicator);
} else {
    addMediaIndicator();
}

// Also check when navigating in SPAs
let lastUrl = location.href;
new MutationObserver(() => {
    const url = location.href;
    if (url !== lastUrl) {
        lastUrl = url;
        setTimeout(addMediaIndicator, 1000); // Delay to let page load
    }
}).observe(document, { subtree: true, childList: true });