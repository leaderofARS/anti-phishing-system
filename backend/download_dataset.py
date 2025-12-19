"""
Download and prepare cybersecurity dataset from Kaggle
"""
import kagglehub
import pandas as pd
import os
from pathlib import Path

def download_dataset():
    """Download the cybersecurity dataset from Kaggle"""
    print("Downloading cybersecurity dataset from Kaggle...")
    print("This may take a few minutes...")
    
    try:
        # Download latest version
        path = kagglehub.dataset_download("macisalvsalv/cybersecurity-dataset")
        print(f"✓ Dataset downloaded to: {path}")
        return path
    except Exception as e:
        print(f"✗ Error downloading dataset: {e}")
        print("\nNote: You may need to:")
        print("1. Install kagglehub: pip install kagglehub")
        print("2. Set up Kaggle API credentials")
        print("3. Visit: https://www.kaggle.com/docs/api")
        return None

def explore_dataset(dataset_path):
    """Explore the downloaded dataset"""
    if not dataset_path:
        return
    
    print("\n" + "="*60)
    print("EXPLORING DATASET")
    print("="*60)
    
    # List all files in the dataset
    dataset_dir = Path(dataset_path)
    files = list(dataset_dir.glob("**/*"))
    
    print(f"\nFound {len(files)} files:")
    for file in files:
        if file.is_file():
            size_mb = file.stat().st_size / (1024 * 1024)
            print(f"  - {file.name} ({size_mb:.2f} MB)")
    
    # Try to load CSV files
    csv_files = list(dataset_dir.glob("**/*.csv"))
    
    if csv_files:
        print(f"\n\nFound {len(csv_files)} CSV file(s)")
        
        for csv_file in csv_files:
            print(f"\n{'='*60}")
            print(f"FILE: {csv_file.name}")
            print('='*60)
            
            try:
                # Try different separators
                for sep in [',', ';', '\t']:
                    try:
                        df = pd.read_csv(csv_file, sep=sep, nrows=5)
                        if df.shape[1] > 1:  # Found correct separator
                            print(f"\n✓ Using separator: '{sep}'")
                            break
                    except:
                        continue
                
                print(f"\nShape: {df.shape}")
                print(f"Columns: {list(df.columns)}")
                print(f"\nFirst 5 rows:")
                print(df.head())
                
                # Show data types
                print(f"\nData types:")
                print(df.dtypes)
                
                # Show missing values
                print(f"\nMissing values:")
                print(df.isnull().sum())
                
            except Exception as e:
                print(f"Error reading {csv_file.name}: {e}")
    else:
        print("\nNo CSV files found in dataset")

def prepare_phishing_data(dataset_path):
    """Prepare data for phishing detection model"""
    if not dataset_path:
        return None
    
    print("\n" + "="*60)
    print("PREPARING DATA FOR ML MODEL")
    print("="*60)
    
    dataset_dir = Path(dataset_path)
    csv_files = list(dataset_dir.glob("**/*.csv"))
    
    if not csv_files:
        print("No CSV files found")
        return None
    
    # Try to find phishing-related data
    for csv_file in csv_files:
        try:
            # Try different separators
            df = None
            for sep in [',', ';', '\t']:
                try:
                    df = pd.read_csv(csv_file, sep=sep)
                    if df.shape[1] > 1:  # Found correct separator
                        print(f"\n✓ Using separator: '{sep}'")
                        break
                except:
                    continue
            
            if df is None or df.shape[1] <= 1:
                print(f"✗ Could not parse {csv_file.name}")
                continue
            
            # Check if this looks like phishing data
            columns_lower = [col.lower() for col in df.columns]
            
            if any(keyword in ' '.join(columns_lower) for keyword in 
                   ['phish', 'url', 'malicious', 'legitimate', 'label', 'threat']):
                
                print(f"\n✓ Found potential phishing dataset: {csv_file.name}")
                print(f"  Shape: {df.shape}")
                print(f"  Columns: {list(df.columns)[:10]}")  # Show first 10 columns
                
                # Save to ml_models directory
                output_dir = Path("app/ml_models/data")
                output_dir.mkdir(parents=True, exist_ok=True)
                
                output_file = output_dir / "phishing_dataset.csv"
                df.to_csv(output_file, index=False)
                
                print(f"\n✓ Saved to: {output_file}")
                
                return output_file
                
        except Exception as e:
            print(f"Error processing {csv_file.name}: {e}")
    
    print("\nNo phishing-related dataset found")
    return None

if __name__ == "__main__":
    print("="*60)
    print("KAGGLE DATASET DOWNLOADER")
    print("="*60)
    
    # Download dataset
    dataset_path = download_dataset()
    
    if dataset_path:
        # Explore the dataset
        explore_dataset(dataset_path)
        
        # Prepare for ML
        prepared_file = prepare_phishing_data(dataset_path)
        
        if prepared_file:
            print("\n" + "="*60)
            print("SUCCESS!")
            print("="*60)
            print(f"\nDataset ready for training at:")
            print(f"  {prepared_file}")
            print("\nNext steps:")
            print("  1. Review the data structure")
            print("  2. Run: python train_model.py")
            print("  3. The trained model will be used automatically")
        else:
            print("\n" + "="*60)
            print("MANUAL SETUP NEEDED")
            print("="*60)
            print("\nThe dataset structure doesn't match expected format.")
            print("Please review the files and adjust the code accordingly.")
    else:
        print("\n" + "="*60)
        print("DOWNLOAD FAILED")
        print("="*60)
        print("\nPlease set up Kaggle API credentials:")
        print("  1. Go to https://www.kaggle.com/settings")
        print("  2. Create API token (downloads kaggle.json)")
        print("  3. Place kaggle.json in ~/.kaggle/ (Linux/Mac)")
        print("     or C:\\Users\\<username>\\.kaggle\\ (Windows)")
