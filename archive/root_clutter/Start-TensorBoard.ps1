# Activate virtual environment
& "C:\Genesis_System3\venv\Scripts\Activate.ps1"

Write-Host "=== Upgrading pip, setuptools, wheel ==="
python -m pip install --upgrade pip setuptools wheel

Write-Host "=== Upgrading TensorBoard ==="
python -m pip install --upgrade tensorboard

Write-Host "=== Attempting to start TensorBoard ==="
try {
    python -m tensorboard.main --logdir=./logs --port=6006
} catch {
    Write-Host "TensorBoard failed with current setup. Applying fallback..."

    # Fallback: downgrade setuptools to avoid ImpImporter issue
    python -m pip install setuptools==68.0.0

    Write-Host "Retrying TensorBoard after downgrade..."
    python -m tensorboard.main --logdir=./logs --port=6006
}
