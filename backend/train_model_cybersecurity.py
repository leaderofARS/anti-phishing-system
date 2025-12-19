"""
Train phishing detection model with cybersecurity dataset
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
        print(f"✗ Dataset not found at: {data_file}")
        print("\nPlease run: python download_dataset.py first")
        return None
    
    print(f"✓ Loading dataset from: {data_file}")
    df = pd.read_csv(data_file)
    
    print(f"\nDataset shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    
    return df

def engineer_features(df):
    """Engineer features from the cybersecurity dataset"""
    print("\n" + "="*60)
    print("ENGINEERING FEATURES")
    print("="*60)
    
    # Create a copy
    features_df = df.copy()
    
    # Extract URL features from 'id' column (which contains URLs)
    print("\nExtracting URL features...")
    features_df['url'] = features_df['id']
    features_df['url_length'] = features_df['url'].str.len()
    features_df['domain_length'] = features_df['url'].apply(lambda x: len(urlparse(str(x)).netloc))
    features_df['has_ip'] = features_df['url'].str.contains(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', regex=True).astype(int)
    features_df['num_dots'] = features_df['url'].str.count('\.')
    features_df['num_hyphens'] = features_df['url'].str.count('-')
    features_df['num_underscores'] = features_df['url'].str.count('_')
    features_df['num_slashes'] = features_df['url'].str.count('/')
    
    # Use existing features from dataset
    feature_columns = [
        'url_length',
        'domain_length',
        'has_ip',
        'num_dots',
        'num_hyphens',
        'num_underscores',
        'num_slashes',
        'reputation',  # From dataset
        'stats_malicious',  # From dataset
        'stats_suspicious',  # From dataset
        'stats_harmless',  # From dataset
        'votes_malicious',  # From dataset
        'malware',  # From dataset
        'phishing',  # From dataset (this is a feature, not label)
        'spam',  # From dataset
    ]
    
    # Create label from threat_status
    # whitelist = 0 (safe), blacklist = 1 (phishing/malicious)
    features_df['label'] = (features_df['threat_status'] != 'whitelist').astype(int)
    
    print(f"\n✓ Created {len(feature_columns)} features")
    print(f"\nLabel distribution:")
    print(features_df['label'].value_counts())
    print(f"\nThreat status distribution:")
    print(features_df['threat_status'].value_counts())
    
    # Select features and label
    X = features_df[feature_columns].fillna(0)
    y = features_df['label']
    
    return X, y, feature_columns

def train_model(X, y, feature_names):
    """Train Random Forest model"""
    print("\n" + "="*60)
    print("TRAINING MODEL")
    print("="*60)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"\nTraining set: {X_train.shape}")
    print(f"Test set: {X_test.shape}")
    
    # Train Random Forest
    print("\nTraining Random Forest Classifier...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=20,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
        class_weight='balanced'  # Handle imbalanced data
    )
    
    model.fit(X_train, y_train)
    
    print("✓ Training complete!")
    
    # Evaluate
    print("\n" + "="*60)
    print("MODEL EVALUATION")
    print("="*60)
    
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)
    
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
    
    # Create directory
    model_dir = Path("app/ml_models/saved_models")
    model_dir.mkdir(parents=True, exist_ok=True)
    
    # Save model
    model_file = model_dir / "phishing_detector.pkl"
    joblib.dump(model, model_file)
    print(f"\n✓ Model saved to: {model_file}")
    
    # Save feature names
    features_file = model_dir / "feature_names.json"
    with open(features_file, 'w') as f:
        json.dump(feature_names, f)
    print(f"✓ Features saved to: {features_file}")
    
    # Save metadata
    metadata = {
        'accuracy': float(accuracy),
        'n_features': len(feature_names),
        'feature_names': feature_names,
        'model_type': 'RandomForestClassifier',
        'dataset': 'cybersecurity-dataset (Kaggle)'
    }
    
    metadata_file = model_dir / "model_metadata.json"
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"✓ Metadata saved to: {metadata_file}")
    
    print("\n" + "="*60)
    print("SUCCESS!")
    print("="*60)
    print("\nModel is ready to use!")
    print("\nNext steps:")
    print("  1. Update backend/app/main.py to load this model")
    print("  2. Restart the backend server")
    print("  3. Test with real URLs!")

if __name__ == "__main__":
    print("="*60)
    print("PHISHING DETECTION MODEL TRAINER")
    print("Using Cybersecurity Dataset from Kaggle")
    print("="*60)
    
    # Load dataset
    df = load_dataset()
    
    if df is not None:
        # Engineer features
        X, y, feature_names = engineer_features(df)
        
        if X is not None:
            # Train model
            model, accuracy, feature_names = train_model(X, y, feature_names)
            
            # Save model
            save_model(model, feature_names, accuracy)
        else:
            print("\n✗ Feature engineering failed")
    else:
        print("\n✗ Dataset loading failed")
        print("Run: python download_dataset.py first")
