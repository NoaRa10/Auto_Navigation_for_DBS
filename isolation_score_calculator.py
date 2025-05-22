import matlab.engine
import numpy as np
from typing import Dict, List

class IsolationScoreCalculator:
    def __init__(self):
        """Initialize the MATLAB engine and add required paths."""
        print("Starting MATLAB engine...")
        self.eng = matlab.engine.start_matlab()
        self.eng.addpath('ISO')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("\nClosing MATLAB engine...")
        self.eng.quit()

    def calculate_isolation_scores(self, raw_analog: List[float], spike_indices: List[int]) -> Dict[str, float]:
        """
        Calculate isolation scores for a given signal and its spike indices.
        
        Parameters:
        -----------
        raw_analog : List[float]
            The filtered signal data
        spike_indices : List[int]
            Indices of detected spikes
            
        Returns:
        --------
        Dict[str, float]
            Dictionary containing the calculated scores
        """
        # Convert to numpy arrays and ensure they're 1D
        raw_analog = np.array(raw_analog).ravel()
        spike_indices = np.array(spike_indices).ravel()

        # Convert to MATLAB format
        matlab_raw_analog = matlab.double(raw_analog.tolist())
        matlab_ap_index = matlab.double(spike_indices.tolist())

        [snr_ap, _, fn_score, fp_score, isolation_score1, *_] = self.eng.test_sorting_IsoDist(
            matlab_raw_analog, matlab_ap_index, float(1), nargout=12)

        return {
            'snr_ap': float(snr_ap) if not self.eng.isnan(snr_ap) else None,
            'fn_score': float(fn_score) if not self.eng.isnan(fn_score) else None,
            'fp_score': float(fp_score) if not self.eng.isnan(fp_score) else None,
            'isolation_score': float(isolation_score1) if not self.eng.isnan(isolation_score1) else None
        } 