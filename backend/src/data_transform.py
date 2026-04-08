import pandas as pd
import yaml
import re
from pathlib import Path
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk
import sys

# Download required NLTK data
nltk.download('punkt_tab', quiet=True)
nltk.download('stopwords', quiet=True)


def load_config(config_path='params.yaml'):
    """Load configuration from YAML file."""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config or {}
    except (FileNotFoundError, yaml.YAMLError):
        return {}


def clean_text(text):
    """
    Advanced text cleaning for phishing detection:
    1. Remove URLs but keep domain info
    2. Normalize whitespace and special patterns
    3. Convert to lowercase
    4. Tokenize and remove stopwords
    5. Keep important phishing indicators (currency, numbers)
    """
    if not isinstance(text, str):
        return ""
    
    # Replace URLs with URL token to preserve URL presence signal
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', 'URL', text)
    
    # Replace email addresses with EMAIL token
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 'EMAIL', text)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove special characters but keep alphanumeric, space, and special tokens
    text = re.sub(r'[^a-z0-9\s$€£¥%()[\]\-]', ' ', text)
    
    # Normalize repeated characters (e.g., "!!!!" -> "!")
    text = re.sub(r'(.)\1{2,}', r'\1', text)
    
    # Tokenize
    tokens = word_tokenize(text)
    
    # Remove stopwords but keep important phishing indicators
    stop_words = set(stopwords.words('english'))
    important_tokens = {'url', 'email', 'click', 'verify', 'confirm', 'urgent', 'act', 'now', 'expire'}
    
    tokens = [
        token for token in tokens 
        if (token not in stop_words or token in important_tokens) and len(token) > 1
    ]
    
    return " ".join(tokens)


def transform_data(input_path, output_path=None):
    """
    Transform raw email dataset by adding cleaned_text column.
    
    Args:
        input_path: Path to raw CSV file
        output_path: Path to save transformed data (optional)
    
    Returns:
        pd.DataFrame: Transformed dataframe
    """
    # Load raw data
    df = pd.read_csv(input_path)
    
    print(f"Loaded {len(df)} records from {input_path}")
    print(f"Columns: {list(df.columns)}")
    
    # Apply text cleaning
    df['cleaned_text'] = df['text'].apply(clean_text)
    
    print(f"\nTransformation complete. Added 'cleaned_text' column.")
    
    # Save transformed data if output path is provided
    if output_path:
        # Create directory if it doesn't exist
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        df.to_csv(output_path, index=False)
        print(f"Saved transformed data to {output_path}")
    
    return df


def get_data_paths():
    """Get data paths from config or use defaults."""
    config = load_config('params.yaml')
    
    # Try to get paths from config
    if config and 'data' in config:
        raw_path = config['data'].get('raw_path')
        processed_path = config['data'].get('processed_path')
    else:
        raw_path = None
        processed_path = None
    
    # Use defaults if not in config
    if not raw_path:
        raw_path = 'backend/data/raw/email_dataset.csv'
    if not processed_path:
        processed_path = 'backend/data/processed/email_dataset_processed.csv'
    
    return raw_path, processed_path


def main():
    """Main execution function."""
    # Get data paths
    raw_path, processed_path = get_data_paths()
    
    # Convert to absolute paths if they're relative
    if not Path(raw_path).is_absolute():
        raw_path = Path.cwd() / raw_path
    if not Path(processed_path).is_absolute():
        processed_path = Path.cwd() / processed_path
    
    print(f"Raw data path: {raw_path}")
    print(f"Processed data path: {processed_path}")
    
    # Verify raw data exists
    if not raw_path.exists():
        print(f"ERROR: Raw data file not found at {raw_path}")
        sys.exit(1)
    
    # Transform data
    df = transform_data(str(raw_path), str(processed_path))
    
    # Display sample
    print("\nSample of transformed data:")
    print(df[['text', 'cleaned_text']].head())
    
    return df


if __name__ == '__main__':
    main()

