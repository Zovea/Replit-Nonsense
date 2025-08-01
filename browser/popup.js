// Popup script for Media Processor Chrome Extension

document.addEventListener('DOMContentLoaded', function() {
    const currentUrlDiv = document.getElementById('currentUrl');
    const sendButton = document.getElementById('sendButton');
    const copyButton = document.getElementById('copyButton');
    const statusDiv = document.getElementById('status');
    const setupLink = document.getElementById('setupLink');
    
    let currentUrl = '';
    
    // Get current tab URL
    chrome.runtime.sendMessage({ action: 'getCurrentUrl' }, function(response) {
        if (response && response.url) {
            currentUrl = response.url;
            currentUrlDiv.textContent = currentUrl;
        } else {
            currentUrlDiv.textContent = 'Unable to get current URL';
        }
    });
    
    // Send button click handler
    sendButton.addEventListener('click', function() {
        if (!currentUrl) {
            showStatus('No URL to send', 'error');
            return;
        }
        
        showStatus('Sending to Media Processor...', 'info');
        
        chrome.runtime.sendMessage({ 
            action: 'sendUrl', 
            url: currentUrl 
        }, function(response) {
            if (response && response.success) {
                showStatus('URL sent successfully!', 'success');
                
                // Close popup after a short delay
                setTimeout(() => {
                    window.close();
                }, 1500);
            } else {
                showStatus('Failed to send URL. Check if Media Processor is running.', 'error');
            }
        });
    });
    
    // Copy button click handler
    copyButton.addEventListener('click', function() {
        if (!currentUrl) {
            showStatus('No URL to copy', 'error');
            return;
        }
        
        const protocolUrl = `mediaprocessor://${encodeURIComponent(currentUrl)}`;
        
        // Copy to clipboard
        navigator.clipboard.writeText(protocolUrl).then(function() {
            showStatus('Protocol link copied to clipboard!', 'success');
        }).catch(function(err) {
            // Fallback: create a text area and copy
            const textArea = document.createElement('textarea');
            textArea.value = protocolUrl;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            
            showStatus('Protocol link copied to clipboard!', 'success');
        });
    });
    
    // Setup link click handler
    setupLink.addEventListener('click', function() {
        chrome.tabs.create({
            url: chrome.runtime.getURL('setup.html')
        });
    });
    
    // Show status message
    function showStatus(message, type) {
        statusDiv.textContent = message;
        statusDiv.className = `status ${type}`;
        statusDiv.style.display = 'block';
        
        // Hide status after 3 seconds for success/info messages
        if (type === 'success' || type === 'info') {
            setTimeout(() => {
                statusDiv.style.display = 'none';
            }, 3000);
        }
    }
    
    // Handle keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            sendButton.click();
        } else if (e.key === 'Escape') {
            window.close();
        }
    });
});