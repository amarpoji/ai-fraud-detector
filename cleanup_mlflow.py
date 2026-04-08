import os
import shutil
from pathlib import Path

# Clean up corrupted MLflow database
db_file = Path("mlflow.db")
mlruns_dir = Path("mlruns")

if db_file.exists():
    os.remove(db_file)
    print(f"✓ Deleted {db_file}")

if mlruns_dir.exists():
    shutil.rmtree(mlruns_dir)
    print(f"✓ Deleted {mlruns_dir}")

print("\n✓ MLflow database cleaned up")
print("\nNext steps:")
print("1. Run training: python backend/src/training.py")
print("2. Then run evaluation: python backend/src/evaluation.py")
