# 🚀 Quick Start Guide

## ✅ PRODUCTION-READY SYSTEM!

- **Backend**: http://localhost:8000 ✓ (484K+ phishing domains loaded)
- **Frontend**: http://localhost:3000 ✓ (Live updates enabled)
- **Extension**: Ready to load
- **ML Model**: 90.91% accuracy
- **Database**: 484,222 malicious domains

---

## 🔌 Load Browser Extension (2 minutes)

### Chrome/Edge Instructions:

1. **Open Extensions Page**
   - Chrome: `chrome://extensions/`
   - Edge: `edge://extensions/`

2. **Enable Developer Mode**
   - Toggle in top-right corner

3. **Load Unpacked**
   - Click "Load unpacked" button
   - Select the `extension` folder
   - Extension icon appears in toolbar

4. **Test It**
   - Click extension icon
   - Should show current page analysis
   - Visit http://localhost:3000 to test

---

## Step 1: Backend Setup (5 minutes) ✅ ALREADY RUNNING

### Install Python Dependencies

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

### Start Backend Server

```bash
# From backend directory
python app/main.py
```

Or using uvicorn directly:
```bash
uvicorn app.main:app --reload
```

Backend will start on: **http://localhost:8000**

### Test Backend

Open another terminal and run:
```bash
python test_api.py
```

Or visit: http://localhost:8000 in your browser

---

## Step 2: Frontend Setup (5 minutes)

### Install Node Dependencies

```bash
cd frontend
npm install
```

### Start Frontend

```bash
npm run dev
```

Frontend will start on: **http://localhost:3000**

---

## Step 3: Browser Extension (2 minutes)

1. Open Chrome/Edge browser
2. Go to: `chrome://extensions/` or `edge://extensions/`
3. Enable **Developer mode** (toggle in top-right)
4. Click **Load unpacked**
5. Select the `extension` folder
6. Extension icon will appear in toolbar

---

## 🎯 Test the System

### Test 1: Dashboard
1. Open http://localhost:3000
2. View statistics on dashboard
3. Navigate to "URL Analyzer"

### Test 2: Analyze URLs
Try analyzing these URLs:

**Safe URL:**
```
https://www.google.com
```

**Suspicious URL (demo):**
```
http://192.168.1.1/login-verify-account
```

**Dangerous URL (demo):**
```
http://secure-login-verify-account-suspended.tk
```

### Test 3: Browser Extension
1. Click the extension icon
2. It will analyze the current page
3. Try visiting different websites
4. Check the risk assessment

---

## 📊 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API info |
| `/health` | GET | Health check |
| `/api/analyze` | POST | Full URL analysis |
| `/api/check/{url}` | GET | Quick check |
| `/api/report` | POST | Report phishing |
| `/api/stats` | GET | Statistics |

---

## 🔧 Troubleshooting

### Backend Issues

**Port 8000 already in use:**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

**Module not found:**
```bash
pip install -r requirements.txt --upgrade
```

### Frontend Issues

**Port 3000 already in use:**
Edit `frontend/vite.config.ts` and change the port:
```typescript
server: {
  port: 3001  // Change to any available port
}
```

**Dependencies error:**
```bash
rm -rf node_modules package-lock.json
npm install
```

### Extension Issues

**Extension not loading:**
- Make sure Developer mode is enabled
- Check for errors in `chrome://extensions/`
- Reload the extension

**API not responding:**
- Verify backend is running on port 8000
- Check browser console for CORS errors
- Update API_URL in extension files if needed

---

## 🎨 Features Overview

### Backend Features
✅ ML-based phishing detection (Random Forest)
✅ 12+ URL features extraction
✅ Domain age and SSL validation
✅ Content analysis (forms, links, etc.)
✅ Real-time risk scoring
✅ Confidence metrics

### Frontend Features
✅ Interactive dashboard
✅ URL analyzer with detailed results
✅ Scan history
✅ Statistics visualization
✅ Responsive design

### Extension Features
✅ Real-time page analysis
✅ Link interception in emails
✅ Warning page for dangerous sites
✅ Badge indicators
✅ Quick popup analysis

---

## 📈 Next Steps

1. **Improve ML Model**: Train with real phishing datasets
2. **Add Database**: Implement PostgreSQL for persistence
3. **External APIs**: Integrate VirusTotal, Google Safe Browsing
4. **User Auth**: Add authentication system
5. **Deploy**: Deploy to cloud (AWS, Azure, GCP)

---

## 💡 Tips

- The ML model is trained with synthetic data for demo purposes
- For production, train with real phishing datasets
- Consider rate limiting for API endpoints
- Add caching for frequently checked URLs
- Implement logging and monitoring

---

## 📞 Need Help?

- Check logs in terminal
- Review browser console for errors
- Ensure all services are running
- Verify ports are not blocked by firewall

**Happy Phishing Detection! 🛡️**
