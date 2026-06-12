"""
Phase 249 Extended: Model Loader & Wrapper

Purpose:
  - Load saved model state dicts from Phase 249 and reconstruct full models
  - Provide consistent model interface for evaluation and online learning
  - Handle model versioning and compatibility

Status: OPERATIONAL
Date: 2025-12-06
"""

import torch
import torch.nn as nn
from pathlib import Path
from typing import Tuple, Any


class SimpleLSTM(nn.Module):
    """Reconstructed LSTM model matching Phase 249 architecture."""

    def __init__(self, input_size: int, hidden_size: int = 64, num_layers: int = 2, num_classes: int = 2):
        """
        Initialize SimpleLSTM model.

        Args:
            input_size: Number of input features
            hidden_size: LSTM hidden size
            num_layers: Number of LSTM layers
            num_classes: Number of output classes
        """
        super(SimpleLSTM, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True, dropout=0.2)
        self.fc = nn.Linear(hidden_size, num_classes)

    def forward(self, x):
        """Forward pass."""
        out, _ = self.lstm(x)
        out = self.fc(out[:, -1, :])  # Take last timestamp
        return out


def load_model_from_state_dict(model_path: Path, input_size: int = 10) -> Tuple[Any, bool]:
    """
    Load a Phase 249 saved model (state dict) and reconstruct full model.

    Args:
        model_path: Path to .pth file
        input_size: Number of input features (should be 10 for Phase 249)

    Returns:
        (model, success_flag)
    """
    if not model_path.exists():
        return None, False

    try:
        # Load state dict
        state_dict = torch.load(model_path, weights_only=False)

        # Reconstruct model with correct architecture
        model = SimpleLSTM(input_size=input_size, hidden_size=64, num_layers=2, num_classes=2)
        model.load_state_dict(state_dict)
        model.eval()

        return model, True
    except Exception as e:
        print(f"Error loading model: {e}")
        return None, False


def main():
    """Test model loading."""
    model_path = Path("c:/Genesis_System3/core/models/dhan/NIFTY_lstm_model.pth")
    model, success = load_model_from_state_dict(model_path)

    if success:
        print(f"✓ Model loaded successfully")
        print(f"  Model type: {type(model)}")
        print(f"  Model structure:\n{model}")
    else:
        print("✗ Failed to load model")


if __name__ == "__main__":
    main()
