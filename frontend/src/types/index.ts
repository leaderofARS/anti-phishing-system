export interface URLAnalysis {
  id?: number;
  url: string;
  risk_score: number;
  risk_level: 'safe' | 'suspicious' | 'dangerous';
  confidence: number;
  features?: Record<string, any>;
  recommendations?: string[];
  allow_access?: boolean;
  scan_time: number;
  timestamp?: string;
}

export interface Stats {
  total_scans: number;
  phishing_detected: number;
  safe_urls: number;
  suspicious_urls: number;
}
