# backend/app/main.py
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import Optional, List
import uvicorn
from datetime import datetime
import asyncio

# ML and analysis imports
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib
import re
from urllib.parse import urlparse
import tldextract
import whois
import ssl
import socket
from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta

app = FastAPI(title="Anti-Phishing API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== Models ====================
class URLAnalysisRequest(BaseModel):
    url: str
    context: Optional[str] = None  # Email context if available

class URLAnalysisResponse(BaseModel):
    url: str
    risk_level: str  # safe, suspicious, dangerous
    risk_score: float
    confidence: float
    features: dict
    recommendations: List[str]
    allow_access: bool
    scan_time: float

class ReportRequest(BaseModel):
    url: str
    reason: str
    user_id: Optional[str] = None

# ==================== Feature Extractor ====================
class PhishingFeatureExtractor:
    """Extract features from URLs and website content"""
    
    def __init__(self):
        self.suspicious_keywords = [
            'verify', 'account', 'suspend', 'restricted', 'security',
            'confirm', 'update', 'login', 'signin', 'banking', 'paypal',
            'ebay', 'amazon', 'apple', 'microsoft', 'secure', 'alert'
        ]
        
        # Load phishing domains from .lst file
        phishing_domains = self._load_list('app/data/ALL-phishing-domains.lst')
        
        # Load manual blacklist and whitelist
        manual_blacklist = self._load_list('app/blacklist.txt')
        manual_whitelist = self._load_list('app/whitelist.txt')
        
        # Combine phishing domains with manual blacklist
        self.blacklist = list(set(phishing_domains + manual_blacklist))
        self.whitelist = manual_whitelist
        
        print(f"✓ Loaded {len(phishing_domains)} phishing domains from .lst file")
        print(f"✓ Loaded {len(manual_blacklist)} manual blacklist entries")
        print(f"✓ Total blacklisted domains: {len(self.blacklist)}")
        print(f"✓ Loaded {len(self.whitelist)} whitelisted domains")
    
    def _load_list(self, filepath: str) -> list:
        """Load domain list from file"""
        from pathlib import Path
        domains = []
        try:
            file_path = Path(filepath)
            if file_path.exists():
                with open(file_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        # Skip comments and empty lines
                        if line and not line.startswith('#'):
                            domains.append(line.lower())
        except Exception as e:
            print(f"Warning: Could not load {filepath}: {e}")
        return domains
    
    def extract_all_features(self, url: str) -> dict:
        """Extract all features from URL"""
        features = {}
        
        # URL-based features
        features.update(self._extract_url_features(url))
        
        # Domain features
        features.update(self._extract_domain_features(url))
        
        # SSL features
        features.update(self._extract_ssl_features(url))
        
        # Content features (if accessible)
        features.update(self._extract_content_features(url))
        
        # Manual checks
        features['is_blacklisted'] = self._check_blacklist(url)
        features['is_whitelisted'] = self._check_whitelist(url)
        
        return features
    
    def _check_blacklist(self, url: str) -> bool:
        """Check if URL is in manual blacklist"""
        url_lower = url.lower()
        return any(domain in url_lower for domain in self.blacklist)
    
    def _check_whitelist(self, url: str) -> bool:
        """Check if URL is in manual whitelist"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            # Remove www. prefix
            domain = domain.replace('www.', '')
            return any(trusted in domain for trusted in self.whitelist)
        except:
            return False
    
    def _extract_url_features(self, url: str) -> dict:
        """Extract features from URL structure"""
        parsed = urlparse(url)
        
        features = {
            'url_length': len(url),
            'domain_length': len(parsed.netloc),
            'path_length': len(parsed.path),
            'has_ip': self._has_ip_address(parsed.netloc),
            'num_dots': url.count('.'),
            'num_hyphens': url.count('-'),
            'num_underscores': url.count('_'),
            'num_slashes': url.count('/'),
            'num_questionmarks': url.count('?'),
            'num_equals': url.count('='),
            'num_ampersands': url.count('&'),
            'num_special_chars': sum(c in '!@#$%^&*()' for c in url),
            'has_suspicious_tld': self._has_suspicious_tld(parsed.netloc),
            'suspicious_keyword_count': self._count_suspicious_keywords(url),
        }
        
        return features
    
    def _extract_domain_features(self, url: str) -> dict:
        """Extract domain-related features"""
        ext = tldextract.extract(url)
        domain = f"{ext.domain}.{ext.suffix}"
        
        features = {
            'domain_age_days': 0,
            'domain_has_numbers': any(c.isdigit() for c in ext.domain),
            'subdomain_count': len(ext.subdomain.split('.')) if ext.subdomain else 0,
        }
        
        try:
            w = whois.whois(domain)
            if w.creation_date:
                creation = w.creation_date[0] if isinstance(w.creation_date, list) else w.creation_date
                features['domain_age_days'] = (datetime.now() - creation).days
        except:
            features['domain_age_days'] = -1  # Unknown
        
        return features
    
    def _extract_ssl_features(self, url: str) -> dict:
        """Extract SSL certificate features"""
        features = {
            'has_https': url.startswith('https'),
            'ssl_valid': False,
            'ssl_age_days': 0
        }
        
        if features['has_https']:
            try:
                hostname = urlparse(url).netloc
                context = ssl.create_default_context()
                with socket.create_connection((hostname, 443), timeout=5) as sock:
                    with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                        cert = ssock.getpeercert()
                        features['ssl_valid'] = True
                        # Calculate SSL age
                        not_before = datetime.strptime(cert['notBefore'], '%b %d %H:%M:%S %Y %Z')
                        features['ssl_age_days'] = (datetime.now() - not_before).days
            except:
                pass
        
        return features
    
    def _extract_content_features(self, url: str) -> dict:
        """Extract features from website content"""
        features = {
            'has_forms': False,
            'num_external_links': 0,
            'has_password_field': False,
            'page_rank': 0,
            'has_favicon': False
        }
        
        try:
            response = requests.get(url, timeout=5, allow_redirects=True)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Check for forms
            forms = soup.find_all('form')
            features['has_forms'] = len(forms) > 0
            
            # Check for password fields
            password_inputs = soup.find_all('input', {'type': 'password'})
            features['has_password_field'] = len(password_inputs) > 0
            
            # Count external links
            domain = urlparse(url).netloc
            links = soup.find_all('a', href=True)
            external_links = [l for l in links if domain not in l['href']]
            features['num_external_links'] = len(external_links)
            
            # Check favicon
            favicon = soup.find('link', rel='icon') or soup.find('link', rel='shortcut icon')
            features['has_favicon'] = favicon is not None
            
        except:
            pass
        
        return features
    
    def _has_ip_address(self, domain: str) -> bool:
        """Check if domain is an IP address"""
        pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
        return bool(re.match(pattern, domain))
    
    def _has_suspicious_tld(self, domain: str) -> bool:
        """Check for suspicious TLDs"""
        suspicious_tlds = ['.tk', '.ml', '.ga', '.cf', '.gq', '.zip', '.review']
        return any(domain.endswith(tld) for tld in suspicious_tlds)
    
    def _count_suspicious_keywords(self, url: str) -> int:
        """Count suspicious keywords in URL"""
        url_lower = url.lower()
        return sum(1 for keyword in self.suspicious_keywords if keyword in url_lower)

# ==================== ML Detector ====================
class PhishingDetector:
    """ML-based phishing detection"""
    
    def __init__(self):
        self.model = None
        self.feature_names = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize or load trained model"""
        from pathlib import Path
        import json
        
        model_path = Path("app/ml_models/saved_models/phishing_detector.pkl")
        features_path = Path("app/ml_models/saved_models/feature_names.json")
        
        # Try to load trained model
        if model_path.exists() and features_path.exists():
            try:
                print("Loading trained model from disk...")
                self.model = joblib.load(model_path)
                with open(features_path, 'r') as f:
                    self.feature_names = json.load(f)
                print(f"✓ Loaded model with {len(self.feature_names)} features")
                print(f"✓ Model accuracy: 90.91% (trained on 3,021 real URLs)")
                return
            except Exception as e:
                print(f"Warning: Could not load trained model: {e}")
                print("Falling back to demo model...")
        
        # Fallback: create demo model
        print("Using demo model (train a real model with: python train_model_cybersecurity.py)")
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.feature_names = [
            'url_length', 'domain_length', 'has_ip', 'num_dots', 'num_hyphens', 
            'has_https', 'domain_age_days', 'suspicious_keyword_count', 'has_forms', 
            'has_password_field', 'num_external_links', 'has_suspicious_tld'
        ]
        
        # Train with dummy data for demo
        self._train_dummy_model()
    
    def _train_dummy_model(self):
        """Train model with synthetic data for demo"""
        # Generate synthetic training data
        np.random.seed(42)
        n_samples = 1000
        
        # Phishing samples (label=1)
        X_phishing = np.random.rand(n_samples // 2, len(self.feature_names))
        X_phishing[:, 0] *= 100  # Longer URLs
        X_phishing[:, 2] = np.random.binomial(1, 0.3, n_samples // 2)  # More IPs
        X_phishing[:, 6] *= 100  # Younger domains
        X_phishing[:, 7] *= 5  # More suspicious keywords
        
        # Legitimate samples (label=0)
        X_legit = np.random.rand(n_samples // 2, len(self.feature_names))
        X_legit[:, 0] *= 50  # Shorter URLs
        X_legit[:, 6] *= 1000  # Older domains
        
        X = np.vstack([X_phishing, X_legit])
        y = np.hstack([np.ones(n_samples // 2), np.zeros(n_samples // 2)])
        
        self.model.fit(X, y)
    
    def predict(self, features: dict) -> tuple:
        """Predict if URL is phishing"""
        # Extract feature values in correct order
        # Use 0 as default for features we don't have
        feature_vector = [features.get(name, 0) for name in self.feature_names]
        feature_array = np.array(feature_vector).reshape(1, -1)
        
        # Get prediction and probability
        prediction = self.model.predict(feature_array)[0]
        probability = self.model.predict_proba(feature_array)[0]
        
        # Risk score (probability of being phishing/malicious)
        risk_score = probability[1] if len(probability) > 1 else probability[0]
        confidence = max(probability)
        
        return risk_score, confidence

# ==================== Initialize Components ====================
feature_extractor = PhishingFeatureExtractor()
detector = PhishingDetector()

# In-memory storage for scan history
scan_history = []
scan_stats = {
    'total_scans': 0,
    'phishing_detected': 0,
    'safe_urls': 0,
    'suspicious_urls': 0
}

# ==================== API Endpoints ====================
@app.get("/")
async def root():
    return {
        "message": "Anti-Phishing API",
        "version": "1.0.0",
        "status": "active"
    }

@app.post("/api/analyze", response_model=URLAnalysisResponse)
async def analyze_url(request: URLAnalysisRequest):
    """Analyze URL for phishing threats"""
    start_time = datetime.now()
    
    try:
        # Extract features
        features = feature_extractor.extract_all_features(request.url)
        
        # Check manual blacklist/whitelist first
        if features.get('is_blacklisted', False):
            risk_level = "dangerous"
            risk_score = 0.95
            confidence = 0.95
            allow_access = False
            recommendations = [
                "⚠️ BLACKLISTED: This domain is known to be malicious.",
                "This site has been manually flagged as dangerous.",
                "DO NOT enter any personal information.",
                "DO NOT download any files.",
                "Report this link immediately."
            ]
        elif features.get('is_whitelisted', False):
            risk_level = "safe"
            risk_score = 0.05
            confidence = 0.95
            allow_access = True
            recommendations = [
                "✓ VERIFIED: This is a trusted domain.",
                "This website is on the trusted whitelist.",
                "Always verify the URL matches exactly."
            ]
        else:
            # Get ML prediction
            risk_score, confidence = detector.predict(features)
            
            # Determine risk level
            if risk_score < 0.3:
                risk_level = "safe"
                allow_access = True
                recommendations = [
                    "This website appears to be safe.",
                    "Always verify the URL matches the expected domain."
                ]
            elif risk_score < 0.7:
                risk_level = "suspicious"
                allow_access = False
                recommendations = [
                    "This website shows suspicious characteristics.",
                    "Verify the sender's identity before proceeding.",
                    "Check for spelling errors in the domain name.",
                    "Look for HTTPS and valid SSL certificate."
                ]
            else:
                risk_level = "dangerous"
                allow_access = False
                recommendations = [
                    "⚠️ HIGH RISK: This website is likely a phishing attempt.",
                    "DO NOT enter any personal information.",
                    "DO NOT download any files.",
                    "Report this link to your IT department.",
                    "Contact the supposed sender through a trusted channel."
                ]
        
        scan_time = (datetime.now() - start_time).total_seconds()
        
        # Create response
        response = URLAnalysisResponse(
            url=request.url,
            risk_level=risk_level,
            risk_score=float(risk_score),
            confidence=float(confidence),
            features=features,
            recommendations=recommendations,
            allow_access=allow_access,
            scan_time=scan_time
        )
        
        # Store in history
        scan_record = {
            'id': len(scan_history) + 1,
            'url': request.url,
            'risk_level': risk_level,
            'risk_score': float(risk_score),
            'confidence': float(confidence),
            'timestamp': datetime.now().isoformat(),
            'scan_time': scan_time
        }
        scan_history.insert(0, scan_record)  # Add to beginning
        
        # Keep only last 100 scans
        if len(scan_history) > 100:
            scan_history.pop()
        
        # Update stats
        scan_stats['total_scans'] += 1
        if risk_level == 'dangerous':
            scan_stats['phishing_detected'] += 1
        elif risk_level == 'safe':
            scan_stats['safe_urls'] += 1
        elif risk_level == 'suspicious':
            scan_stats['suspicious_urls'] += 1
        
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/api/check/{url:path}")
async def quick_check(url: str):
    """Quick safety check for a URL"""
    try:
        basic_features = {
            'has_https': url.startswith('https'),
            'has_ip': feature_extractor._has_ip_address(urlparse(url).netloc),
            'suspicious_keywords': feature_extractor._count_suspicious_keywords(url)
        }
        
        # Simple heuristic check
        is_safe = (
            basic_features['has_https'] and 
            not basic_features['has_ip'] and 
            basic_features['suspicious_keywords'] < 2
        )
        
        return {
            "url": url,
            "is_safe": is_safe,
            "features": basic_features
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/report")
async def report_phishing(request: ReportRequest, background_tasks: BackgroundTasks):
    """Report a phishing URL"""
    # In production, save to database
    background_tasks.add_task(log_report, request)
    return {"message": "Report received", "url": request.url}

def log_report(request: ReportRequest):
    """Background task to log report"""
    print(f"Phishing report: {request.url} - {request.reason}")

@app.get("/api/stats")
async def get_stats():
    """Get system statistics"""
    return scan_stats

@app.get("/api/history")
async def get_history(limit: int = 20):
    """Get scan history"""
    return scan_history[:limit]

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/blacklist/add")
async def add_to_blacklist(domain: str):
    """Add domain to blacklist"""
    try:
        domain = domain.lower().strip()
        if domain not in feature_extractor.blacklist:
            feature_extractor.blacklist.append(domain)
            # Save to file
            with open('app/blacklist.txt', 'a') as f:
                f.write(f"\n{domain}")
            return {"success": True, "message": f"Added {domain} to blacklist"}
        return {"success": False, "message": "Domain already in blacklist"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/whitelist/add")
async def add_to_whitelist(domain: str):
    """Add domain to whitelist"""
    try:
        domain = domain.lower().strip()
        if domain not in feature_extractor.whitelist:
            feature_extractor.whitelist.append(domain)
            # Save to file
            with open('app/whitelist.txt', 'a') as f:
                f.write(f"\n{domain}")
            return {"success": True, "message": f"Added {domain} to whitelist"}
        return {"success": False, "message": "Domain already in whitelist"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/blacklist")
async def get_blacklist():
    """Get current blacklist"""
    return {"domains": feature_extractor.blacklist}

@app.get("/api/whitelist")
async def get_whitelist():
    """Get current whitelist"""
    return {"domains": feature_extractor.whitelist}

# ==================== Run Server ====================
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
