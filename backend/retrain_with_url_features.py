"""
Retrain model using only URL-extractable features
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib
from pathlib import Path
import json
from urllib.parse import urlparse

def load_dataset():
    """Load the cybersecurity dataset"""
    data_file = Path("app/ml_models/data/phishing_dataset.csv")
    
    if not data_file.exists():
        print(f"✗ Dataset not found")
        return None
    
    print(f"✓ Loading dataset...")
    df = pd.read_csv(data_file)
    print(f"  Shape: {df.shape}")
    
    return df

def engineer_url_only_features(df):
    """Engineer features that can be extracted from URL alone"""
    print("\n" + "="*60)
    print("ENGINEERING URL-ONLY FEATURES")
    print("="*60)
    
    features_df = df.copy()
    
    # Extract URL features from 'id' column
    print("\nExtracting URL features...")
    features_df['url'] = features_df['id']
    features_df['url_length'] = features_df['url'].str.len()
    features_df['domain_length'] = features_df['url'].apply(lambda x: len(urlparse(str(x)).netloc))
    features_df['path_length'] = features_df['url'].apply(lambda x: len(urlparse(str(x)).path))
    features_df['has_ip'] = features_df['url'].str.contains(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', regex=True).astype(int)
    features_df['num_dots'] = features_df['url'].str.count(r'\.')
    features_df['num_hyphens'] = features_df['url'].str.count('-')
    features_df['num_underscores'] = features_df['url'].str.count('_')
    features_df['num_slashes'] = features_df['url'].str.count('/')
    features_df['num_questionmarks'] = features_df['url'].str.count(r'\?')
    features_df['num_equals'] = features_df['url'].str.count('=')
    features_df['num_ampersands'] = features_df['url'].str.count('&')
    features_df['num_special_chars'] = features_df['url'].apply(lambda x: sum(c in '!@#$%^&*()' for c in str(x)))
    
    # Check for suspicious TLDs
    suspicious_tlds = ['.tk', '.ml', '.ga', '.cf', '.gq', '.zip', '.review']
    features_df['has_suspicious_tld'] = features_df['url'].apply(
        lambda x: int(any(str(x).endswith(tld) for tld in suspicious_tlds))
    )
    
    # Count suspicious keywords
    suspicious_keywords = [
        'verify', 'account', 'suspend', 'restricted', 'security',
        'confirm', 'update', 'login', 'signin', 'banking', 'paypal'
    ]
    features_df['suspicious_keyword_count'] = features_df['url'].apply(
        lambda x: sum(1 for keyword in suspicious_keywords if keyword in str(x).lower())
    )
    
    # These features match what PhishingFeatureExtractor provides
    feature_columns = [
        'url_length',
        'domain_length',
        'path_length',
        'has_ip',
        'num_dots',
        'num_hyphens',
        'num_underscores',
        'num_slashes',
        'num_questionmarks',
        'num_equals',
        'num_ampersands',
        'num_special_chars',
        'has_suspicious_tld',
        'suspicious_keyword_count',
    ]
    
    # Create label
    features_df['label'] = (features_df['threat_status'] != 'whitelist').astype(int)
    
    print(f"\n✓ Created {len(feature_columns)} URL-based features")
    print(f"\nLabel distribution:")
    print(features_df['label'].value_counts())
    
    X = features_df[feature_columns].fillna(0)
    y = features_df['label']
    
    return X, y, feature_columns

def train_model(X, y, feature_names):
    """Train Random Forest model"""
    print("\n" + "="*60)
    print("TRAINING MODEL")
    print("="*60)
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"\nTraining set: {X_train.shape}")
    print(f"Test set: {X_test.shape}")
    
    print("\nTraining Random Forest Classifier...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=20,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
        class_weight='balanced'
    )
    
    model.fit(X_train, y_train)
    print("✓ Training complete!")
    
    # Evaluate
    print("\n" + "="*60)
    print("MODEL EVALUATION")
    print("="*60)
    
    y_pred = model.predict(X_test)
    
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\nAccuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
    
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['Safe', 'Malicious']))
    
    print("\nConfusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print(cm)
    print(f"\nTrue Negatives: {cm[0][0]}")
    print(f"False Positives: {cm[0][1]}")
    print(f"False Negatives: {cm[1][0]}")
    print(f"True Positives: {cm[1][1]}")
    
    # Feature importance
    print("\nTop 10 Most Important Features:")
    feature_importance = pd.DataFrame({
        'feature': feature_names,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print(feature_importance.head(10).to_string(index=False))
    
    return model, accuracy, feature_names

def save_model(model, feature_names, accuracy):
    """Save trained model"""
    print("\n" + "="*60)
    print("SAVING MODEL")
    print("="*60)
    
    model_dir = Path("app/ml_models/saved_models")
    model_dir.mkdir(parents=True, exist_ok=True)
    
    model_file = model_dir / "phishing_detector.pkl"
    joblib.dump(model, model_file)
    print(f"\n✓ Model saved to: {model_file}")
    
    features_file = model_dir / "feature_names.json"
    with open(features_file, 'w') as f:
        json.dump(feature_names, f)
    print(f"✓ Features saved to: {features_file}")
    
    metadata = {
        'accuracy': float(accuracy),
        'n_features': len(feature_names),
        'feature_names': feature_names,
        'model_type': 'RandomForestClassifier',
        'dataset': 'cybersecurity-dataset (Kaggle)',
        'features_type': 'URL-only (no external APIs needed)'
    }
    
    metadata_file = model_dir / "model_metadata.json"
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"✓ Metadata saved to: {metadata_file}")
    
    print("\n" + "="*60)
    print("SUCCESS!")
    print("="*60)
    print("\nModel trained with URL-only features!")
    print("This model works with features extracted by PhishingFeatureExtractor")
    print("\nRestart the backend to load the new model.")

if __name__ == "__main__":
    print("="*60)
    print("RETRAINING WITH URL-ONLY FEATURES")
    print("="*60)
    
    df = load_dataset()
    
    if df is not None:
        X, y, feature_names = engineer_url_only_features(df)
        
        if X is not None:
            model, accuracy, feature_names = train_model(X, y, feature_names)
            save_model(model, feature_names, accuracy)
    else:
        print("\n✗ Dataset loading failed")
