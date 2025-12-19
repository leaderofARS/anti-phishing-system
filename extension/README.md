# PhishGuard - Anti-Phishing Browser Extension

## 🛡️ Features

- **Real-time Protection**: Analyzes URLs before you visit them
- **484K+ Phishing Database**: Checks against massive known phishing domain list
- **Email Link Protection**: Intercepts suspicious links in Gmail, Outlook, Yahoo Mail
- **Beautiful UI**: Modern modal dialogs with risk assessment
- **Smart Caching**: Reduces API calls for better performance
- **Desktop Notifications**: Alerts for dangerous sites

## 📦 Installation

### Chrome/Edge

1. Open your browser
2. Navigate to:
   - Chrome: `chrome://extensions/`
   - Edge: `edge://extensions/`
3. Enable **Developer mode** (toggle in top-right)
4. Click **Load unpacked**
5. Select the `extension` folder
6. Extension icon appears in toolbar (will use default icon)

**Note**: The extension uses browser's default icon. You can add custom icons later by creating:
- `icons/icon16.png` (16x16)
- `icons/icon48.png` (48x48)
- `icons/icon128.png` (128x128)

## 🚀 Usage

### Automatic Protection
- Extension automatically analyzes pages as you browse
- Shows badge with risk level (✓ Safe, ! Suspicious, ⛔ Dangerous)
- Desktop notification for dangerous sites

### Manual Check
1. Click extension icon
2. View current page analysis
3. See risk score, confidence, and recommendations

### Email Protection
1. Open Gmail/Outlook/Yahoo Mail
2. Click any link in an email
3. Beautiful modal shows risk assessment
4. Choose to proceed or go back

## 🎨 Risk Levels

### ✓ Safe (Green)
- Risk score: 0-30%
- Trusted domain or clean URL structure
- Safe to proceed

### ⚠️ Suspicious (Yellow)
- Risk score: 30-70%
- Some suspicious characteristics
- Proceed with caution

### ⛔ Dangerous (Red)
- Risk score: 70-100%
- Known phishing domain or high-risk patterns
- DO NOT proceed

## 🔧 Configuration

### Change Backend URL

If your backend is on a different port/server:

**Edit `background.js`:**
```javascript
const API_URL = 'http://your-server:8000/api';
```

**Edit `popup/popup.js`:**
```javascript
const API_URL = 'http://your-server:8000/api';
```

## 📊 Features

### Blacklist/Whitelist
- ✅ 484,220 known phishing domains
- ✅ Manual blacklist for custom entries
- ✅ Whitelist for trusted domains
- ✅ Instant detection

### ML Analysis
- ✅ 90.91% accuracy
- ✅ 14 URL features analyzed
- ✅ Real-time prediction
- ✅ Confidence scoring

### User Interface
- ✅ Color-coded risk levels
- ✅ Detailed recommendations
- ✅ Blacklist/whitelist badges
- ✅ Scan time display
- ✅ One-click dashboard access

## 🔐 Privacy

- URLs are sent to your local backend only (localhost:8000)
- No data sent to external servers
- Analysis results cached locally
- No personal information collected

## 🐛 Troubleshooting

### Extension not working
- Ensure backend is running: `http://localhost:8000`
- Check browser console (F12) for errors
- Reload extension from extensions page

### API connection failed
- Verify backend server is running
- Check if port 8000 is accessible
- Ensure no firewall blocking

### Badge not showing
- Refresh the page
- Check if URL is analyzable (not chrome:// pages)
- Reload extension

## 📝 Files

```
extension/
├── manifest.json       # Extension configuration
├── background.js       # Background service worker
├── content.js         # Content script (page injection)
├── popup/
│   ├── popup.html     # Extension popup UI
│   └── popup.js       # Popup logic
└── icons/             # Extension icons
```

## 🎯 Supported Email Clients

- ✅ Gmail (mail.google.com)
- ✅ Outlook (outlook.live.com, outlook.office.com)
- ✅ Yahoo Mail (mail.yahoo.com)
- ✅ ProtonMail (protonmail.com)

## 🔄 Updates

To update the extension:
1. Make changes to files
2. Go to `chrome://extensions/`
3. Click reload icon on extension
4. Test changes

## 📞 Support

For issues:
- Check backend is running
- Review browser console logs
- Verify extension permissions
- Check API endpoint configuration

---

**Protected by 484K+ phishing domains! 🛡️**
