import json
from pathlib import Path
import numpy as np
from typing import Dict, Optional, Tuple
from scipy import signal

class SignalProcessor:
    def __init__(self, data_dir: str):
        """
        Initialize the SignalProcessor with the directory containing extracted data.
        
        Args:
            data_dir (str): Path to the directory containing extracted data files
        """
        self.data_dir = Path(data_dir)
        if not self.data_dir.exists():
            raise FileNotFoundError(f"Data directory {data_dir} not found")
            
    def load_subject_data(self, subject_file: str) -> Dict:
        """
        Load a subject's data from a JSON file.
        
        Args:
            subject_file (str): Name of the subject's data file
            
        Returns:
            Dict: Loaded subject data
        """
        file_path = self.data_dir / (f"{subject_file}_extracted.json")
        if not file_path.exists():
            raise FileNotFoundError(f"Subject file {subject_file} not found")
            
        with open(file_path, 'r') as f:
            return json.load(f)
            
    def convert_to_millivolts(self, raw_signal: np.ndarray, metadata: Dict) -> np.ndarray:
        """
        Convert raw signal to millivolts using bit resolution and gain from metadata.
        
        Args:
            raw_signal (np.ndarray): Raw signal data
            metadata (Dict): Subject metadata containing bit resolution and gain
            
        Returns:
            np.ndarray: Signal in millivolts
        """
        bit_resolution = metadata['BitResolution']
        gain = metadata['Gain']
        signal_array = np.array(raw_signal, dtype=float)
        return (signal_array * bit_resolution) / gain

    def apply_bandpass_filter(self, signal_data: np.ndarray, sampling_rate: float, 
                            low_freq: float, high_freq: float, order: int = 4) -> np.ndarray:
        """
        Apply a non-causal bandpass Butterworth filter to the signal.
        This keeps frequencies within the specified range and removes frequencies outside it.
        
        Args:
            signal_data (np.ndarray): Input signal
            sampling_rate (float): Sampling rate in Hz
            low_freq (float): Lower cutoff frequency in Hz
            high_freq (float): Higher cutoff frequency in Hz
            order (int): Filter order (default: 4)
            
        Returns:
            np.ndarray: Filtered signal
        """
        # Normalize frequencies by Nyquist frequency
        nyquist = sampling_rate / 2
        low = low_freq / nyquist
        high = high_freq / nyquist
        
        # Design filter
        b, a = signal.butter(order, [low, high], btype='band')
        
        # Apply filter using filtfilt to avoid phase shift
        filtered_signal = signal.filtfilt(b, a, signal_data)
        
        return filtered_signal
        
    def process_subject(self, subject_name: str, filter_band: Optional[Tuple[float, float]] = None) -> Dict:
        """
        Process a single subject's data.
        
        Args:
            subject_name (str): Name of the subject
            filter_band (tuple, optional): (low_freq, high_freq) for bandpass filtering
            
        Returns:
            dict: Processed data with the following structure:
            {
                'subject_metadata': {
                    'subject_name': str,
                    'sampling_rate': float,
                    'filter_band': Optional[tuple]
                },
                'samples': {
                    'sample_name': {
                        'signal_mv': List[float],  # Signal in millivolts
                        'filtered_signal': Optional[List[float]],  # Filtered signal if filter_band provided
                        'metadata': {
                            'sample_name': str,
                            'duration': float,
                            'num_points': int
                        }
                    }
                }
            }
        """
        # Load subject data
        subject_data = self.load_subject_data(subject_name)
        if not subject_data:
            return {}
            
        # Get metadata
        metadata = subject_data['subject_metadata']
        sampling_rate = metadata['KHz'] * 1000  # Convert KHz to Hz
        
        # Process each sample
        processed_samples = {}
        for sample_name, sample_data in subject_data['samples'].items():
            # Convert raw signal to millivolts
            signal_mv = self.convert_to_millivolts(
                np.array(sample_data['raw_signal']),
                metadata
            )
            
            # Apply filter if specified
            filtered_signal = None
            if filter_band:
                filtered_signal = self.apply_bandpass_filter(
                    signal_mv,
                    sampling_rate,
                    filter_band[0],
                    filter_band[1]
                )
            
            # Store processed data
            processed_samples[sample_name] = {
                'signal_mv': signal_mv.tolist(),
                'filtered_signal': filtered_signal.tolist() if filtered_signal is not None else None,
                'metadata': {
                    'sample_name': sample_name,
                    'duration': len(signal_mv) / sampling_rate,
                    'num_points': len(signal_mv)
                }
            }
        
        # Create processed data structure
        processed_data = {
            'subject_metadata': {
                'subject_name': subject_name,
                'sampling_rate': sampling_rate,
                'filter_band': filter_band
            },
            'samples': processed_samples
        }
        
        return processed_data
        
    def process_all_subjects(self, output_dir: str = "processed_signals", 
                           filter_band: Optional[Tuple[float, float]] = None) -> Dict:
        """
        Process all subjects in the data directory.
        
        Args:
            output_dir (str): Directory to save processed data
            filter_band (Optional[Tuple[float, float]]): Optional tuple of (low_freq, high_freq) for bandpass filtering
            
        Returns:
            Dict: Dictionary mapping subject names to their processed data file paths
        """
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        processed_files = {}
        for subject_file in self.data_dir.glob("*_extracted.json"):
            try:
                subject_name = subject_file.stem.replace('_extracted', '')
                # Process subject data
                processed_data = self.process_subject(subject_name, filter_band)
                
                # Create filename based on whether filtering was applied
                if filter_band is not None:
                    low_freq, high_freq = filter_band
                    output_file = output_path / f"{subject_name}_processed_{int(low_freq)}-{int(high_freq)}Hz.json"
                else:
                    output_file = output_path / f"{subject_name}_processed.json"
                
                # Save processed data
                with open(output_file, 'w') as f:
                    json.dump(processed_data, f, indent=4)
                    
                processed_files[subject_name] = str(output_file)
                print(f"Processed signals for {subject_name}")
                
            except Exception as e:
                print(f"Error processing {subject_file.name}: {str(e)}")
                
        return processed_files 