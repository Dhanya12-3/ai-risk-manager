import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.ml.pipeline import train
if __name__ == '__main__':
    train()
