const API_URL = 'http://localhost:8000/api';
const CACHE_DURATION = 3600000; // 1 hour

// In-memory cache for analyzed URLs
const urlCache = new Map();

// Listen for messages from content script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'analyzeUrl') {
    analyzeUrl(request.url).then(sendResponse);
    return true; // Will respond asynchronously
  }
  
  if (request.action === 'reportPhishing') {
    reportPhishing(request.url, request.reason).then(sendResponse);
    return true;
  }
  
  if (request.action === 'getStats') {
    getStats().then(sendResponse);
    return true;
  }
});

// Analyze URL with caching
async function analyzeUrl(url) {
  try {
    // Check cache first
    const cached = urlCache.get(url);
    if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
      console.log('Returning cached result for:', url);
      return cached.result;
    }
    
    // Call API
    const response = await fetch(`${API_URL}/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url })
    });
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    
    const result = await response.json();
    
    // Cache result
    urlCache.set(url, {
      result,
      timestamp: Date.now()
    });
    
    // Update badge based on risk level
    updateBadge(result.risk_level);
    
    // Log to storage
    await logScan(url, result);
    
    // Show notification for dangerous sites
    if (result.risk_level === 'dangerous') {
      chrome.notifications.create({
        type: 'basic',
        title: '⚠️ Phishing Warning',
        message: `Dangerous site detected: ${url.substring(0, 50)}...`,
        priority: 2
      });
    }
    
    return result;
  } catch (error) {
    console.error('Error analyzing URL:', error);
    return {
      error: true,
      message: 'Failed to analyze URL. Make sure backend is running on port 8000.',
      risk_level: 'unknown',
      risk_score: 0,
      confidence: 0,
      recommendations: ['Could not connect to analysis server']
    };
  }
}

// Report phishing URL
async function reportPhishing(url, reason) {
  try {
    const response = await fetch(`${API_URL}/report`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url, reason })
    });
    
    return await response.json();
  } catch (error) {
    console.error('Error reporting phishing:', error);
    return { error: true, message: 'Failed to submit report' };
  }
}

// Get statistics
async function getStats() {
  try {
    const response = await fetch(`${API_URL}/stats`);
    const apiStats = await response.json();
    
    // Get local stats from storage
    const local = await chrome.storage.local.get(['scans', 'blocked']);
    
    return {
      ...apiStats,
      localScans: local.scans || 0,
      localBlocked: local.blocked || 0
    };
  } catch (error) {
    console.error('Error getting stats:', error);
    return { error: true };
  }
}

// Update extension badge
function updateBadge(riskLevel) {
  const colors = {
    safe: '#10B981',
    suspicious: '#F59E0B',
    dangerous: '#EF4444',
    unknown: '#6B7280'
  };
  
  chrome.action.setBadgeBackgroundColor({ color: colors[riskLevel] || colors.unknown });
  chrome.action.setBadgeText({ text: '!' });
}

// Log scan to storage
async function logScan(url, result) {
  const { scans = [], blocked = 0 } = await chrome.storage.local.get(['scans', 'blocked']);
  
  const scan = {
    id: Date.now().toString(),
    url,
    risk_level: result.risk_level,
    risk_score: result.risk_score,
    timestamp: new Date().toISOString()
  };
  
  // Keep only last 50 scans
  const updatedScans = [scan, ...scans].slice(0, 50);
  const updatedBlocked = result.risk_level === 'dangerous' ? blocked + 1 : blocked;
  
  await chrome.storage.local.set({ 
    scans: updatedScans,
    blocked: updatedBlocked
  });
}

// Clear old cache entries periodically
setInterval(() => {
  const now = Date.now();
  for (const [url, data] of urlCache.entries()) {
    if (now - data.timestamp > CACHE_DURATION) {
      urlCache.delete(url);
    }
  }
}, 600000); // Every 10 minutes
