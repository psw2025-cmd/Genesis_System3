"""
LSTM-based time-series forecasting for option chain / spot / IV (Governance Responsibility 6).
Optional: requires torch. Used for volatility and price movement predictions when data is available.
"""
from typing import List, Optional

# Optional torch
try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    torch = None
    nn = None


def _get_device():
    if not TORCH_AVAILABLE:
        return None
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


class LSTMForecaster(nn.Module if TORCH_AVAILABLE else object):
    """Simple LSTM for univariate time-series (e.g. spot close, IV series)."""

    def __init__(self, input_size: int = 1, hidden_size: int = 32, num_layers: int = 1, output_size: int = 1):
        if TORCH_AVAILABLE:
            super().__init__()
        else:
            return
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        if not TORCH_AVAILABLE:
            return None
        out, _ = self.lstm(x)
        return self.fc(out[:, -1, :])


def forecast_series(series: List[float], steps: int = 5, seq_len: int = 20) -> Optional[List[float]]:
    """
    Forecast next steps using a simple LSTM (or fallback to last-value).
    series: historical values (e.g. spot prices or IV)
    steps: number of steps to predict
    seq_len: sequence length for LSTM
    """
    if not series or len(series) < 2:
        return None
    if not TORCH_AVAILABLE or len(series) < seq_len:
        # Fallback: repeat last value
        return [float(series[-1])] * steps
    device = _get_device()
    model = LSTMForecaster(1, 32, 1, 1).to(device)  # type: ignore
    # Minimal forward pass for demo (no training in this stub)
    seq = series[-seq_len:]
    x = torch.tensor([seq], dtype=torch.float32).unsqueeze(-1).to(device)
    with torch.no_grad():
        pred = model(x)
    if pred is None:
        return [float(series[-1])] * steps
    out = [pred.item()]
    for _ in range(steps - 1):
        out.append(out[-1])
    return out


def is_available() -> bool:
    return TORCH_AVAILABLE
