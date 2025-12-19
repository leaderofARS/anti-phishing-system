const API_URL = 'http://localhost:8000/api';

document.addEventListener('DOMContentLoaded', async () => {
  const contentDiv = document.getElementById('content');
  
  try {
    // Get current tab
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    if (!tab || !tab.url) {
      showError('Unable to get current tab information');
      return;
    }
    
    const url = tab.url;
    
    // Skip chrome:// pages
    if (url.startsWith('chrome://') || url.startsWith('chrome-extension://')) {
      showInfo('Extension pages are not analyzed');
      return;
    }
    
    // Check if we have cached analysis
    const cached = await chrome.storage.local.get(`analysis_${tab.id}`);
    
    if (cached[`analysis_${tab.id}`]) {
      displayAnalysis(cached[`analysis_${tab.id}`]);
    } else {
      // Perform new analysis
      analyzeCurrentPage(url);
    }
    
  } catch (error) {
    showError(error.message);
  }
});

async function analyzeCurrentPage(url) {
  const contentDiv = document.getElementById('content');
  contentDiv.innerHTML = '<div class="loading">Analyzing page...</div>';
  
  try {
    const response = await fetch(`${API_URL}/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        url: url,
        include_content: true
      })
    });
    
    const result = await response.json();
    displayAnalysis(result);
    
  } catch (error) {
    showError('Failed to analyze page. Make sure the backend is running.');
  }
}

function displayAnalysis(analysis) {
  const contentDiv = document.getElementById('content');
  
  const statusClass = analysis.risk_level || 'unknown';
  const statusText = {
    'safe': '✓ Safe',
    'suspicious': '⚠️ Suspicious',
    'dangerous': '⛔ Dangerous',
    'unknown': '? Unknown'
  }[statusClass];
  
  // Check if it's blacklisted or whitelisted
  const isBlacklisted = analysis.features?.is_blacklisted;
  const isWhitelisted = analysis.features?.is_whitelisted;
  
  let statusBadge = '';
  if (isBlacklisted) {
    statusBadge = '<div style="background: #DC2626; color: white; padding: 4px 8px; border-radius: 4px; font-size: 11px; margin-top: 8px;">🚫 BLACKLISTED</div>';
  } else if (isWhitelisted) {
    statusBadge = '<div style="background: #059669; color: white; padding: 4px 8px; border-radius: 4px; font-size: 11px; margin-top: 8px;">✓ VERIFIED</div>';
  }
  
  contentDiv.innerHTML = `
    <div class="status ${statusClass}">
      <h2>${statusText}</h2>
      <p>Risk Score: ${(analysis.risk_score * 100).toFixed(0)}%</p>
      <p style="font-size: 12px; margin-top: 4px;">Confidence: ${(analysis.confidence * 100).toFixed(1)}%</p>
      ${statusBadge}
    </div>
    
    <div class="info">
      <label>URL:</label>
      <value style="word-break: break-all; font-size: 12px;">${analysis.url}</value>
    </div>
    
    <div class="info">
      <label>Recommendations:</label>
      ${analysis.recommendations.map(r => `<p style="margin: 5px 0; font-size: 13px;">• ${r}</p>`).join('')}
    </div>
    
    <div class="info" style="font-size: 11px; color: #666; margin-top: 8px;">
      <p>Scan time: ${analysis.scan_time?.toFixed(2)}s</p>
      <p>Protected by 484K+ phishing domains</p>
    </div>
    
    <button class="btn-primary" id="reanalyze">Re-analyze</button>
    ${analysis.risk_level !== 'safe' ? '<button class="btn-danger" id="report">Report as Phishing</button>' : ''}
    <button class="btn-secondary" id="viewStats">View Dashboard</button>
  `;
  
  // Add event listeners
  document.getElementById('reanalyze').addEventListener('click', async () => {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    analyzeCurrentPage(tab.url);
  });
  
  const reportBtn = document.getElementById('report');
  if (reportBtn) {
    reportBtn.addEventListener('click', () => {
      reportPhishing(analysis.url);
    });
  }
  
  document.getElementById('viewStats').addEventListener('click', () => {
    chrome.tabs.create({ url: 'http://localhost:3000' });
  });
}

function showError(message) {
  const contentDiv = document.getElementById('content');
  contentDiv.innerHTML = `
    <div class="status unknown">
      <p>⚠️ ${message}</p>
    </div>
  `;
}

function showInfo(message) {
  const contentDiv = document.getElementById('content');
  contentDiv.innerHTML = `
    <div class="status unknown">
      <p>${message}</p>
    </div>
  `;
}

async function reportPhishing(url) {
  try {
    const response = await fetch(`${API_URL}/report`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        url: url,
        reason: 'User reported from extension',
        reported_by: 'extension_user'
      })
    });
    
    const result = await response.json();
    alert(result.message || 'Thank you for reporting!');
    
  } catch (error) {
    alert('Failed to submit report');
  }
}
