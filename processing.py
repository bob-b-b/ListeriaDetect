from collections import deque
import statistics
from typing import Iterable, Optional, Tuple, Dict
import math

class Processor:
    """Hold recent measurements, compute stats and a score.

    Usage:
      p = Processor(window=10, ema_alpha=0.3)
      p.add_frequency(123.4)
      score = p.kanzawa_gordon(p.moving_average(), baseline=130.0)
      is_pos, score = p.detect_listeria(threshold=0.5)
    """

    def __init__(self, window: int = 10, ema_alpha: float = 0.3):
        self.window = max(1, int(window))
        self.buffer = deque(maxlen=self.window)
        self.ema_alpha = float(ema_alpha)
        self._ema: Optional[float] = None

    def add_frequency(self, freq: float) -> float:
        """Add a new frequency sample and update EMA.

        Returns the updated EMA value.
        """
        f = float(freq)
        self.buffer.append(f)
        if self._ema is None:
            self._ema = f
        else:
            self._ema = self.ema_alpha * f + (1 - self.ema_alpha) * self._ema
        return self._ema

    def moving_average(self) -> Optional[float]:
        if not self.buffer:
            return None
        return sum(self.buffer) / len(self.buffer)

    def ema(self) -> Optional[float]:
        return self._ema

    def stats(self) -> Dict[str, Optional[float]]:
        if not self.buffer:
            return {"count": 0, "mean": None, "median": None, "stdev": None, "min": None, "max": None}
        return {
            "count": len(self.buffer),
            "mean": statistics.mean(self.buffer),
            "median": statistics.median(self.buffer),
            "stdev": statistics.stdev(self.buffer) if len(self.buffer) > 1 else 0.0,
            "min": min(self.buffer),
            "max": max(self.buffer),
        }
    
    @staticmethod
    def kanazawa_gordon_delta(f0: float, eta_L: float, rho_L: float, mu_Q: float, rho_Q: float) -> float:
        """Compute the Kanazawa–Gordon predicted frequency shift (Delta f, Hz).

        Formula (Kanazawa & Gordon, 1985):
        https://openqcm.com/openqcm-test-of-quartz-crystal-microbalance-in-contact-with-liquid.html
            Delta f = - f0^(3/2) * sqrt( (eta_L * rho_L) / (pi * mu_Q * rho_Q) )

        Parameters:
          - f0: resonance frequency (Hz)
          - eta_L: viscosity (Pa·s)
          - rho_L: liquid density (kg/m^3)
          - mu_Q: shear modulus of quartz (Pa)
          - rho_Q: density of quartz (kg/m^3)

        Returns negative value (downshift).
        """
        f0 = float(f0)
        numerator = float(eta_L) * float(rho_L)
        denominator = math.pi * float(mu_Q) * float(rho_Q)
        if denominator <= 0 or numerator < 0:
            raise ValueError("Invalid physical parameters for Kanazawa–Gordon calculation")
        delta = - (f0 ** 1.5) * math.sqrt(numerator / denominator)
        return delta

    def detect_listeria(self, freq: Optional[float] = None, baseline: Optional[float] = None,
                        expected_liquid: Optional[Dict[str, float]] = None,
                        threshold_hz: float = 100.0) -> Tuple[bool, float]:
        """Return (is_listeria_present, score) using Kanazawa–Gordon only.

        Parameters
        - freq: measured frequency (Hz). If None, uses EMA or moving average.
        - baseline: control frequency (Hz). If None, moving average is used as baseline.
        - expected_liquid: dict with keys {'f0','eta_L','rho_L','mu_Q','rho_Q'}
        - threshold_hz: absolute Hz tolerance for deciding a mismatch between measured
            delta and theoretical KG delta. If abs(measured_delta - expected_delta) > threshold_hz
            then the sample is flagged (returns True).

        Returns (is_flagged, signed_difference_hz)
        """
        if expected_liquid is None:
            raise ValueError("expected_liquid must be provided for Kanazawa–Gordon based detection")

        if freq is None:
            freq = self.ema() or self.moving_average()
        if freq is None:
            raise ValueError("No frequency data available")

        if baseline is None:
            baseline = self.moving_average()
        if baseline is None:
            raise ValueError("Baseline frequency is required for detection")

        measured_delta = baseline - float(freq)

        expected = Processor.kanazawa_gordon_delta(
            f0=expected_liquid['f0'],
            eta_L=expected_liquid['eta_L'],
            rho_L=expected_liquid['rho_L'],
            mu_Q=expected_liquid['mu_Q'],
            rho_Q=expected_liquid['rho_Q'],
        )

        diff = measured_delta - expected
        is_flagged = abs(diff) > float(threshold_hz)
        return is_flagged, diff


def example_run():
    p = Processor(window=5, ema_alpha=0.25)
    # simulate incoming frequencies
    for f in [100.0, 98.5, 99.2, 97.8, 96.5, 95.0]:
        ema = p.add_frequency(f)
        print(f"Added {f:.1f} Hz -> EMA={ema:.2f}, MA={p.moving_average():.2f}")

    # use a baseline (control) measurement and coefficients chosen experimentally
    baseline = 100.0
    coeffs = {"a": 1.0, "b": 0.0, "c": 0.0}
    is_pos, score = p.detect_listeria(baseline=baseline, coeffs=coeffs, threshold=2.0)
    print(f"Detect listeria? {is_pos} (score={score:.3f})")

    # Example compute Kanazawa–Gordon expected delta for pure water (10 MHz crystal)
    params = {
        'f0': 10e6,
        # viscosity: 1.002e-3 Pa·s (20 °C), density: 998.2 kg/m^3
        'eta_L': 1.002e-3,
        'rho_L': 998.2,
        # quartz shear modulus ~ 2.947e10 Pa, density ~ 2648 kg/m^3
        'mu_Q': 2.947e10,
        'rho_Q': 2648.0,
    }
    expected_delta = Processor.kanazawa_gordon_delta(**params)
    print(f"Kanazawa–Gordon expected delta for water (10 MHz): {expected_delta:.1f} Hz")
    measured_delta = baseline - (baseline + expected_delta)
    print(f"Example measured delta (if sample matched water): {measured_delta:.1f} Hz")


if __name__ == "__main__":
    example_run()
