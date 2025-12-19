(function() {
  'use strict';
  
  console.log('PhishGuard content script loaded');
  
  // Configuration
  const EMAIL_DOMAINS = [
    'mail.google.com',
    'outlook.live.com',
    'outlook.office.com',
    'mail.yahoo.com',
    'protonmail.com'
  ];
  
  const WHITELIST = [
    'google.com',
    'youtube.com',
    'facebook.com',
    'twitter.com',
    'linkedin.com',
    'github.com'
  ];
  
  // Check if we're on an email page
  const isEmailPage = EMAIL_DOMAINS.some(domain => 
    window.location.hostname.includes(domain)
  );
  
  if (isEmailPage) {
    console.log('PhishGuard: Email page detected, monitoring links');
    interceptEmailLinks();
  }
  
  // Intercept all external links
  interceptAllLinks();
  
  function interceptEmailLinks() {
    // Use event delegation for dynamically loaded content
    document.addEventListener('click', async (e) => {
      const link = e.target.closest('a');
      
      if (!link || !link.href) return;
      
      const url = link.href;
      
      // Skip internal links and whitelisted domains
      if (isInternalLink(url) || isWhitelisted(url)) return;
      
      // Prevent default navigation
      e.preventDefault();
      e.stopPropagation();
      
      console.log('PhishGuard: Intercepted link:', url);
      
      // Show loading modal
      showLoadingModal(url);
      
      // Analyze URL
      chrome.runtime.sendMessage(
        { action: 'analyzeUrl', url },
        (result) => {
          hideLoadingModal();
          
          if (result.error) {
            showErrorModal(url, result.message);
          } else {
            showResultModal(url, result);
          }
        }
      );
    }, true); // Use capture phase
  }
  
  function interceptAllLinks() {
    // Also monitor navigation attempts
    window.addEventListener('beforeunload', (e) => {
      // Could add additional checks here
    });
  }
  
  function isInternalLink(url) {
    try {
      const linkHost = new URL(url).hostname;
      const currentHost = window.location.hostname;
      return linkHost === currentHost;
    } catch {
      return true; // Invalid URL, treat as internal
    }
  }
  
  function isWhitelisted(url) {
    try {
      const hostname = new URL(url).hostname;
      return WHITELIST.some(domain => hostname.includes(domain));
    } catch {
      return false;
    }
  }
  
  // Modal functions
  function showLoadingModal(url) {
    const modal = createModal(`
      <div class="phishguard-modal-content">
        <div class="phishguard-spinner"></div>
        <h2>Analyzing Link...</h2>
        <p>PhishGuard is checking if this link is safe</p>
        <div class="phishguard-url">${escapeHtml(url)}</div>
      </div>
    `);
    document.body.appendChild(modal);
  }
  
  function hideLoadingModal() {
    const modal = document.getElementById('phishguard-modal');
    if (modal) modal.remove();
  }
  
  function showResultModal(url, result) {
    const riskColors = {
      safe: { bg: '#ECFDF5', border: '#10B981', text: '#065F46' },
      suspicious: { bg: '#FEF3C7', border: '#F59E0B', text: '#92400E' },
      dangerous: { bg: '#FEE2E2', border: '#EF4444', text: '#991B1B' }
    };
    
    const colors = riskColors[result.risk_level] || riskColors.suspicious;
    const icon = result.risk_level === 'safe' ? '✓' : 
                 result.risk_level === 'suspicious' ? '⚠' : '✗';
    
    const modal = createModal(`
      <div class="phishguard-modal-content" style="background: ${colors.bg}; border-color: ${colors.border};">
        <div class="phishguard-icon" style="color: ${colors.text};">${icon}</div>
        <h2 style="color: ${colors.text};">
          ${result.risk_level.toUpperCase()} - Risk Score: ${(result.risk_score * 100).toFixed(0)}%
        </h2>
        <div class="phishguard-url">${escapeHtml(url)}</div>
        <div class="phishguard-recommendations">
          ${result.recommendations.map(rec => 
            `<div class="phishguard-rec">• ${escapeHtml(rec)}</div>`
          ).join('')}
        </div>
        <div class="phishguard-buttons">
          ${result.allow_access ? 
            `<button class="phishguard-btn phishguard-btn-primary" id="phishguard-proceed">Proceed to Site</button>` :
            `<button class="phishguard-btn phishguard-btn-danger" id="phishguard-proceed">⚠ Proceed Anyway (Not Recommended)</button>`
          }
          <button class="phishguard-btn phishguard-btn-secondary" id="phishguard-close">Go Back to Safety</button>
          ${result.risk_level !== 'safe' ? 
            `<button class="phishguard-btn phishguard-btn-report" id="phishguard-report">Report Phishing</button>` : 
            ''
          }
        </div>
      </div>
    `);
    
    document.body.appendChild(modal);
    
    // Add event listeners after modal is added to DOM
    const proceedBtn = document.getElementById('phishguard-proceed');
    const closeBtn = document.getElementById('phishguard-close');
    const reportBtn = document.getElementById('phishguard-report');
    
    if (proceedBtn) {
      proceedBtn.addEventListener('click', () => {
        hideLoadingModal();
        window.location.href = url;
      });
    }
    
    if (closeBtn) {
      closeBtn.addEventListener('click', () => {
        hideLoadingModal();
      });
    }
    
    if (reportBtn) {
      reportBtn.addEventListener('click', () => {
        const reason = prompt('Please describe why you think this is phishing:');
        if (reason) {
          chrome.runtime.sendMessage(
            { action: 'reportPhishing', url, reason },
            (response) => {
              alert('Thank you for your report!');
              hideLoadingModal();
            }
          );
        }
      });
    }
  }
  
  function showErrorModal(url, message) {
    const modal = createModal(`
      <div class="phishguard-modal-content">
        <div class="phishguard-icon" style="color: #EF4444;">⚠</div>
        <h2>Analysis Failed</h2>
        <p>${escapeHtml(message)}</p>
        <div class="phishguard-url">${escapeHtml(url)}</div>
        <div class="phishguard-buttons">
          <button class="phishguard-btn phishguard-btn-primary" id="phishguard-proceed-error">Proceed Anyway</button>
          <button class="phishguard-btn phishguard-btn-secondary" id="phishguard-close-error">Go Back</button>
        </div>
      </div>
    `);
    
    document.body.appendChild(modal);
    
    // Add event listeners
    document.getElementById('phishguard-proceed-error').addEventListener('click', () => {
      hideLoadingModal();
      window.location.href = url;
    });
    
    document.getElementById('phishguard-close-error').addEventListener('click', () => {
      hideLoadingModal();
    });
  }
  
  function createModal(content) {
    const modal = document.createElement('div');
    modal.id = 'phishguard-modal';
    modal.innerHTML = `
      <style>
        #phishguard-modal {
          position: fixed;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          background: rgba(0, 0, 0, 0.8);
          display: flex;
          justify-content: center;
          align-items: center;
          z-index: 999999;
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }
        .phishguard-modal-content {
          background: white;
          border-radius: 16px;
          padding: 32px;
          max-width: 600px;
          width: 90%;
          box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
          border: 3px solid #E5E7EB;
          text-align: center;
        }
        .phishguard-spinner {
          border: 4px solid #E5E7EB;
          border-top: 4px solid #3B82F6;
          border-radius: 50%;
          width: 50px;
          height: 50px;
          animation: spin 1s linear infinite;
          margin: 0 auto 20px;
        }
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        .phishguard-icon {
          font-size: 64px;
          margin-bottom: 16px;
        }
        .phishguard-modal-content h2 {
          margin: 16px 0;
          font-size: 24px;
          font-weight: bold;
        }
        .phishguard-url {
          background: rgba(0, 0, 0, 0.05);
          padding: 12px;
          border-radius: 8px;
          font-family: monospace;
          word-break: break-all;
          margin: 16px 0;
          font-size: 14px;
        }
        .phishguard-recommendations {
          text-align: left;
          margin: 20px 0;
        }
        .phishguard-rec {
          margin: 8px 0;
          padding-left: 8px;
        }
        .phishguard-buttons {
          display: flex;
          flex-direction: column;
          gap: 12px;
          margin-top: 24px;
        }
        .phishguard-btn {
          padding: 14px 24px;
          border: none;
          border-radius: 8px;
          font-size: 16px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s;
        }
        .phishguard-btn-primary {
          background: #3B82F6;
          color: white;
        }
        .phishguard-btn-primary:hover {
          background: #2563EB;
        }
        .phishguard-btn-danger {
          background: #EF4444;
          color: white;
        }
        .phishguard-btn-danger:hover {
          background: #DC2626;
        }
        .phishguard-btn-secondary {
          background: #E5E7EB;
          color: #374151;
        }
        .phishguard-btn-secondary:hover {
          background: #D1D5DB;
        }
        .phishguard-btn-report {
          background: #F59E0B;
          color: white;
          font-size: 14px;
        }
        .phishguard-btn-report:hover {
          background: #D97706;
        }
      </style>
      ${content}
    `;
    return modal;
  }
  
  // Global functions for modal buttons
  window.phishguardProceed = (url) => {
    hideLoadingModal();
    window.location.href = url;
  };
  
  window.phishguardClose = () => {
    hideLoadingModal();
  };
  
  window.phishguardReport = (url) => {
    const reason = prompt('Please describe why you think this is phishing:');
    if (reason) {
      chrome.runtime.sendMessage(
        { action: 'reportPhishing', url, reason },
        (response) => {
          alert('Thank you for your report!');
          hideLoadingModal();
        }
      );
    }
  };
  
  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
})();
