"""
Extract trained models from MLflow and save as pickle files for inference.
This bridges the gap between MLflow logging and local model loading.
"""

import json
import pickle
import mlflow
import mlflow.sklearn
from pathlib import Path
import sys

def extract_models_from_mlflow():
    """Extract all trained models from MLflow and save locally."""
    
    artifacts_dir = Path('mlflow_artifacts')
    training_info_path = artifacts_dir / 'training_info.json'
    
    if not training_info_path.exists():
        print("❌ training_info.json not found. Run training.py first.")
        return
    
    with open(training_info_path, 'r') as f:
        training_info = json.load(f)
    
    print(f"Found {len(training_info['results'])} trained models")
    
    extracted_count = 0
    failed_count = 0
    
    for result in training_info['results']:
        run_id = result['run_id']
        model_name = result['model_name']
        tfidf_variant = result['tfidf_variant']
        
        model_dir = artifacts_dir / f"{model_name}_{tfidf_variant}"
        model_dir.mkdir(parents=True, exist_ok=True)
        
        model_file = model_dir / "model.pkl"
        vectorizer_file = model_dir / "vectorizer.pkl"
        
        # Skip if already extracted
        if model_file.exists() and vectorizer_file.exists():
            print(f"✓ {model_name}_{tfidf_variant} already extracted")
            continue
        
        try:
            # Load model from MLflow
            model_uri = f"runs:/{run_id}/model"
            model = mlflow.sklearn.load_model(model_uri)
            
            # Save model as pickle
            with open(model_file, 'wb') as f:
                pickle.dump(model, f)
            
            # Try to load vectorizer from MLflow artifacts
            try:
                artifacts = mlflow.artifacts.download_artifacts(run_id=run_id)
                artifacts_path = Path(artifacts)
                
                # Look for vectorizer.pkl in the artifacts directory
                vectorizer_files = list(artifacts_path.glob('**/vectorizer.pkl'))
                
                if vectorizer_files:
                    src_vectorizer = vectorizer_files[0]
                    with open(src_vectorizer, 'rb') as f:
                        vectorizer = pickle.load(f)
                    with open(vectorizer_file, 'wb') as f:
                        pickle.dump(vectorizer, f)
                    print(f"✓ Extracted {model_name}_{tfidf_variant}")
                    extracted_count += 1
                else:
                    print(f"⚠ No vectorizer.pkl found for {run_id}")
                    failed_count += 1
            
            except Exception as e:
                print(f"⚠ Could not extract vectorizer for {model_name}_{tfidf_variant}: {e}")
                # Still save the model even if vectorizer fails
                extracted_count += 1
        
        except Exception as e:
            print(f"❌ Failed to extract {model_name}_{tfidf_variant}: {e}")
            failed_count += 1
    
    print(f"\n{'='*60}")
    print(f"Extraction complete: {extracted_count} models extracted, {failed_count} failed")

if __name__ == "__main__":
    extract_models_from_mlflow()
