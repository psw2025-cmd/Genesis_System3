"""
System3 Phase 341 - Model Drift Detector v2 (Rolling Window) - UPGRADED

Quantifies drift between training distribution and recent live data in detail.
Computes per-feature drift scores, overall drift index, and triggers WARN/ALERT flags.

UPGRADED FEATURES:
- ADWIN (Adaptive Windowing) algorithm for real-time drift detection
- Page-Hinkley test for mean shift detection
- Enhanced drift detection with multiple algorithms
- Real-time streaming drift detection capability

Mode: Post-market, optionally daily pre-market refresh.
"""

import sys
import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Tuple, Optional
import logging
from scipy.spatial import distance
from scipy.stats import ks_2samp
from collections import deque

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

logger = logging.getLogger(__name__)


class ADWIN:
    """
    ADWIN (Adaptive Windowing) algorithm for concept drift detection.

    Detects changes in the mean of a stream by maintaining two windows
    and comparing their means. If the difference exceeds a threshold,
    drift is detected.
    """

    def __init__(self, delta: float = 0.002, min_window_size: int = 5, max_window_size: int = 1000):
        """
        Initialize ADWIN detector.

        Args:
            delta: Confidence level (default 0.002 = 99.8% confidence)
            min_window_size: Minimum window size before drift detection
            max_window_size: Maximum window size
        """
        self.delta = delta
        self.min_window_size = min_window_size
        self.max_window_size = max_window_size
        self.window = deque()
        self.total = 0.0
        self.variance = 0.0
        self.drift_detected = False

    def add_element(self, value: float) -> bool:
        """
        Add a new element to the window and check for drift.

        Args:
            value: New data point

        Returns:
            True if drift detected, False otherwise
        """
        self.window.append(value)
        self.total += value

        # Maintain max window size
        if len(self.window) > self.max_window_size:
            old_value = self.window.popleft()
            self.total -= old_value

        # Check for drift if window is large enough
        if len(self.window) >= self.min_window_size * 2:
            return self._detect_drift()

        return False

    def _detect_drift(self) -> bool:
        """Detect drift using ADWIN algorithm."""
        n = len(self.window)
        if n < self.min_window_size * 2:
            return False

        # Calculate mean and variance
        mean = self.total / n
        variance = np.var(list(self.window)) if n > 1 else 0.0

        # Try different split points
        for split in range(self.min_window_size, n - self.min_window_size + 1):
            window1 = list(self.window)[:split]
            window2 = list(self.window)[split:]

            mean1 = np.mean(window1)
            mean2 = np.mean(window2)
            n1, n2 = len(window1), len(window2)

            # Calculate threshold
            m = 1.0 / (1.0 / n1 + 1.0 / n2)
            delta_prime = self.delta / n
            epsilon_cut = np.sqrt(2.0 / m * variance * np.log(2.0 / delta_prime)) + 2.0 / (3.0 * m) * np.log(
                2.0 / delta_prime
            )

            # Check if means differ significantly
            if abs(mean1 - mean2) > epsilon_cut:
                # Drift detected - reset window
                self.drift_detected = True
                # Keep only recent window
                keep_size = min(n2, self.max_window_size // 2)
                recent = list(self.window)[-keep_size:]
                self.window = deque(recent)
                self.total = sum(recent)
                return True

        self.drift_detected = False
        return False

    def get_mean(self) -> float:
        """Get current mean of the window."""
        if len(self.window) == 0:
            return 0.0
        return self.total / len(self.window)


class PageHinkley:
    """
    Page-Hinkley test for detecting mean shifts in a data stream.

    Monitors the cumulative sum of deviations from the mean and
    detects when the mean has shifted significantly.
    """

    def __init__(self, threshold: float = 10.0, delta: float = 0.005, min_instances: int = 30):
        """
        Initialize Page-Hinkley detector.

        Args:
            threshold: Detection threshold (default 10.0)
            delta: Minimum change to detect (default 0.005)
            min_instances: Minimum instances before detection
        """
        self.threshold = threshold
        self.delta = delta
        self.min_instances = min_instances
        self.values = deque(maxlen=1000)
        self.mean = 0.0
        self.sum_upper = 0.0
        self.sum_lower = 0.0
        self.drift_detected = False

    def add_element(self, value: float) -> bool:
        """
        Add a new element and check for drift.

        Args:
            value: New data point

        Returns:
            True if drift detected, False otherwise
        """
        self.values.append(value)

        if len(self.values) < self.min_instances:
            return False

        # Update running mean
        self.mean = np.mean(list(self.values))

        # Calculate cumulative sums
        deviation = value - self.mean - self.delta
        self.sum_upper = max(0.0, self.sum_upper + deviation)
        self.sum_lower = min(0.0, self.sum_lower + deviation)

        # Check for drift
        if self.sum_upper > self.threshold or abs(self.sum_lower) > self.threshold:
            self.drift_detected = True
            # Reset for next detection
            self.sum_upper = 0.0
            self.sum_lower = 0.0
            return True

        self.drift_detected = False
        return False

    def get_mean(self) -> float:
        """Get current mean."""
        return self.mean


def compute_kl_divergence(p: np.ndarray, q: np.ndarray, bins: int = 20) -> float:
    """
    Compute KL divergence between two distributions using histogram binning.
    Handles edge cases like zero counts.
    """
    try:
        p_hist, _ = np.histogram(p[~np.isnan(p)], bins=bins)
        q_hist, _ = np.histogram(q[~np.isnan(q)], bins=bins)

        p_hist = (p_hist + 1e-6) / (p_hist.sum() + 1e-5)
        q_hist = (q_hist + 1e-6) / (q_hist.sum() + 1e-5)

        return float(np.sum(p_hist * np.log(p_hist / q_hist)))
    except Exception as e:
        logger.warning(f"KL divergence calculation failed: {e}")
        return 0.0


def compute_drift_score(
    baseline: np.ndarray,
    live: np.ndarray,
    adwin_detector: Optional[ADWIN] = None,
    page_hinkley_detector: Optional[PageHinkley] = None,
) -> Dict[str, float]:
    """
    Compute drift score using multiple metrics including ADWIN and Page-Hinkley.
    Returns dict with individual scores and overall drift.

    Args:
        baseline: Baseline distribution
        live: Live data distribution
        adwin_detector: Optional ADWIN detector for streaming detection
        page_hinkley_detector: Optional Page-Hinkley detector for streaming detection
    """
    baseline_clean = baseline[~np.isnan(baseline)]
    live_clean = live[~np.isnan(live)]

    if len(baseline_clean) == 0 or len(live_clean) == 0:
        return {
            "mean_diff_pct": 0.0,
            "std_diff_pct": 0.0,
            "ks_statistic": 0.0,
            "kl_divergence": 0.0,
            "adwin_drift": False,
            "page_hinkley_drift": False,
            "overall_drift": 0.0,
        }

    # Mean difference percentage
    baseline_mean = np.mean(baseline_clean)
    live_mean = np.mean(live_clean)
    mean_diff = abs(live_mean - baseline_mean) / (abs(baseline_mean) + 1e-6) * 100

    # Std difference percentage
    baseline_std = np.std(baseline_clean)
    live_std = np.std(live_clean)
    std_diff = abs(live_std - baseline_std) / (abs(baseline_std) + 1e-6) * 100

    # KS statistic (0-1 range)
    ks_stat, _ = ks_2samp(baseline_clean, live_clean)

    # KL divergence
    kl_div = compute_kl_divergence(baseline_clean, live_clean)

    # ADWIN drift detection (streaming)
    adwin_drift = False
    if adwin_detector is not None:
        for val in live_clean[:100]:  # Sample for efficiency
            if adwin_detector.add_element(float(val)):
                adwin_drift = True
                break
    elif len(live_clean) > 20:
        # Create temporary ADWIN detector
        temp_adwin = ADWIN(delta=0.002, min_window_size=5)
        for val in live_clean[:100]:
            if temp_adwin.add_element(float(val)):
                adwin_drift = True
                break

    # Page-Hinkley drift detection (streaming)
    page_hinkley_drift = False
    if page_hinkley_detector is not None:
        for val in live_clean[:100]:  # Sample for efficiency
            if page_hinkley_detector.add_element(float(val)):
                page_hinkley_drift = True
                break
    elif len(live_clean) > 30:
        # Create temporary Page-Hinkley detector
        temp_ph = PageHinkley(threshold=10.0, delta=0.005, min_instances=30)
        for val in live_clean[:100]:
            if temp_ph.add_element(float(val)):
                page_hinkley_drift = True
                break

    # Overall drift: weighted combination (enhanced with ADWIN/PH flags)
    base_drift = mean_diff * 0.25 + std_diff * 0.25 + ks_stat * 100 * 0.2 + min(kl_div, 100) * 0.15

    # Boost drift score if ADWIN or Page-Hinkley detected drift
    drift_boost = 0.0
    if adwin_drift:
        drift_boost += 15.0  # Significant boost for ADWIN detection
    if page_hinkley_drift:
        drift_boost += 15.0  # Significant boost for Page-Hinkley detection

    overall_drift = base_drift + drift_boost

    return {
        "mean_diff_pct": float(mean_diff),
        "std_diff_pct": float(std_diff),
        "ks_statistic": float(ks_stat),
        "kl_divergence": float(min(kl_div, 100)),
        "adwin_drift": adwin_drift,
        "page_hinkley_drift": page_hinkley_drift,
        "overall_drift": float(overall_drift),
    }


def run_phase_341_model_drift_detector_v2(root_path: str = None, logger_obj=None) -> str:
    """
    Phase 341: Detect model drift by comparing training distribution vs live data.

    Returns: 'OK' or 'WARN'
    """
    if logger_obj:
        logger = logger_obj

    if root_path is None:
        root_path = str(PROJECT_ROOT)

    root = Path(root_path)
    logger.info("[PH341] Starting Model Drift Detector v2")

    try:
        # Paths
        signals_with_forward = root / "storage" / "live" / "angel_index_ai_signals_with_forward.csv"
        diag_dir = root / "storage" / "live" / "diagnostics"
        diag_dir.mkdir(parents=True, exist_ok=True)

        output_file = diag_dir / "model_drift_report.csv"
        model_health_file = diag_dir / "model_health_snapshot.json"

        # Load baseline stats (if saved from training)
        baseline_stats = {}
        try:
            training_stats_file = root / "storage" / "models" / "training_stats.json"
            if training_stats_file.exists():
                with open(training_stats_file) as f:
                    baseline_stats = json.load(f).get("feature_stats", {})
        except Exception as e:
            logger.warning(f"[PH341] Could not load baseline stats: {e}")

        # Load live signals
        if not signals_with_forward.exists():
            logger.warning(f"[PH341] Signals with forward file not found: {signals_with_forward}")
            return "WARN"

        df_live = pd.read_csv(signals_with_forward)

        if df_live.empty:
            logger.warning("[PH341] Live signals dataframe is empty")
            return "WARN"

        # Compute drift per feature (numeric columns only)
        drift_results = {}
        has_drift_warning = False
        drift_threshold = 50.0  # Overall drift score threshold

        # Initialize ADWIN and Page-Hinkley detectors for key features
        key_features = ["delta", "gamma", "theta", "iv", "spot", "ltp", "ai_score"]
        adwin_detectors = {feat: ADWIN(delta=0.002, min_window_size=5) for feat in key_features}
        ph_detectors = {feat: PageHinkley(threshold=10.0, delta=0.005, min_instances=30) for feat in key_features}

        numeric_cols = df_live.select_dtypes(include=[np.number]).columns

        for col in numeric_cols:
            if col in baseline_stats and "mean" in baseline_stats[col]:
                baseline_vals = np.array([baseline_stats[col]["mean"]] * 100)  # Synthetic for comparison
                live_vals = df_live[col].values

                # Get detectors for this feature if available
                adwin_det = adwin_detectors.get(col)
                ph_det = ph_detectors.get(col)

                drift_scores = compute_drift_score(baseline_vals, live_vals, adwin_det, ph_det)
                drift_results[col] = drift_scores

                # Check for drift warnings
                drift_detected = (
                    drift_scores["overall_drift"] > drift_threshold
                    or drift_scores.get("adwin_drift", False)
                    or drift_scores.get("page_hinkley_drift", False)
                )

                if drift_detected:
                    has_drift_warning = True
                    drift_reasons = []
                    if drift_scores["overall_drift"] > drift_threshold:
                        drift_reasons.append(f"overall_drift={drift_scores['overall_drift']:.2f}")
                    if drift_scores.get("adwin_drift", False):
                        drift_reasons.append("ADWIN_detected")
                    if drift_scores.get("page_hinkley_drift", False):
                        drift_reasons.append("PageHinkley_detected")

                    logger.warning(f"[PH341] High drift detected for {col}: {', '.join(drift_reasons)}")
            else:
                # No baseline; use streaming detectors only
                if col in adwin_detectors or col in ph_detectors:
                    live_vals = df_live[col].values
                    adwin_det = adwin_detectors.get(col)
                    ph_det = ph_detectors.get(col)

                    # Check streaming detectors
                    adwin_drift = False
                    ph_drift = False

                    if adwin_det:
                        for val in live_vals[:100]:
                            if adwin_det.add_element(float(val)):
                                adwin_drift = True
                                break

                    if ph_det:
                        for val in live_vals[:100]:
                            if ph_det.add_element(float(val)):
                                ph_drift = True
                                break

                    if adwin_drift or ph_drift:
                        has_drift_warning = True
                        drift_results[col] = {
                            "adwin_drift": adwin_drift,
                            "page_hinkley_drift": ph_drift,
                            "overall_drift": 60.0 if (adwin_drift or ph_drift) else 0.0,
                        }
                        logger.warning(
                            f"[PH341] Streaming drift detected for {col}: "
                            f"ADWIN={adwin_drift}, PageHinkley={ph_drift}"
                        )
                else:
                    # No baseline; log as informational
                    logger.debug(f"[PH341] No baseline for feature {col}, skipping drift check")

        # Write drift report
        if drift_results:
            df_drift = pd.DataFrame.from_dict(drift_results, orient="index")
            df_drift.to_csv(output_file, index_label="feature")
            logger.info(f"[PH341] Drift report written to {output_file}")

        # Update model health snapshot
        if model_health_file.exists():
            with open(model_health_file) as f:
                health = json.load(f)
        else:
            health = {}

        health["drift_detected"] = has_drift_warning
        health["drift_score"] = float(
            np.mean([r["overall_drift"] for r in drift_results.values()]) if drift_results else 0.0
        )
        health["timestamp"] = datetime.now().isoformat()

        with open(model_health_file, "w") as f:
            json.dump(health, f, indent=2)

        status = "WARN" if has_drift_warning else "OK"
        logger.info(f"[PH341] Model Drift Detector v2 complete. Status: {status}")

        return status

    except Exception as e:
        logger.error(f"[PH341] Unexpected error: {e}", exc_info=True)
        return "WARN"


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    result = run_phase_341_model_drift_detector_v2()
    print(f"Phase 341 result: {result}")
