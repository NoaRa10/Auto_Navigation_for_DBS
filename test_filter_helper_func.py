import re
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import SpanSelector
from pathlib import Path
import json
from scipy import signal
import random


def load_data(file_path: str) -> dict:
    """Load data from a JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)

def extract_filter_band(filename: str) -> tuple:
    """
    Extract filter band from filename.
    Expected format: subject_processed_LOW-HIGHHz.json
    
    Args:
        filename (str): Name of the processed file
        
    Returns:
        tuple: (low_freq, high_freq) or None if no filter band found
    """
    match = re.search(r'_(\d+)-(\d+)Hz\.json$', filename)
    if match:
        return (int(match.group(1)), int(match.group(2)))
    return None

def plot_signal_comparison(original_signal: np.ndarray, filtered_signal: np.ndarray, 
                         sampling_rate: float, filter_band: tuple = None,
                         title: str = "Signal Comparison"):
    """
    Plot original and filtered signals in both time and frequency domains with interactive features.
    
    Args:
        original_signal (np.ndarray): Original signal in millivolts
        filtered_signal (np.ndarray): Filtered signal
        sampling_rate (float): Sampling rate in Hz
        filter_band (tuple): Optional tuple of (low_freq, high_freq) for filter band
        title (str): Plot title
    """
    # Ensure signals are numpy arrays and have the correct shape
    original_signal = np.asarray(original_signal, dtype=float).flatten()
    filtered_signal = np.asarray(filtered_signal, dtype=float).flatten()
    
    if len(original_signal) != len(filtered_signal):
        raise ValueError(f"Signal lengths don't match: original={len(original_signal)}, filtered={len(filtered_signal)}")
    
    if len(original_signal) < 2:
        raise ValueError(f"Signal too short: length={len(original_signal)}")
    
    # Create time array
    time = np.arange(len(original_signal)) / sampling_rate
    
    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Plot time domain signals
    ax1.plot(time, original_signal, label='Original (mV)', color='blue', alpha=0.7)
    ax1.plot(time, filtered_signal, label='Filtered (mV)', color='red', alpha=0.7)
    ax1.set_title('Time Domain')
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Amplitude (mV)')
    ax1.legend()
    ax1.grid(True)
    
    # Compute and plot frequency domain using Welch's method
    nperseg = min(256, len(original_signal) // 8)  # Segment length
    noverlap = nperseg // 2  # 50% overlap
    
    # Compute power spectral density
    freqs_orig, psd_orig = signal.welch(original_signal, sampling_rate, 
                                       nperseg=nperseg, noverlap=noverlap)
    freqs_filt, psd_filt = signal.welch(filtered_signal, sampling_rate, 
                                       nperseg=nperseg, noverlap=noverlap)
    
    # Plot frequency domain
    ax2.semilogy(freqs_orig, psd_orig, label='Original', color='blue', alpha=0.7)
    ax2.semilogy(freqs_filt, psd_filt, label='Filtered', color='red', alpha=0.7)
    
    # Add filter band markers if provided
    if filter_band:
        low_freq, high_freq = filter_band
        # Add vertical lines for filter band
        ax2.axvline(x=low_freq, color='green', linestyle='--', alpha=0.5, 
                   label=f'Filter Band: {low_freq}-{high_freq} Hz')
        ax2.axvline(x=high_freq, color='green', linestyle='--', alpha=0.5)
        # Shade the filter band
        ax2.axvspan(low_freq, high_freq, color='green', alpha=0.1)
    
    ax2.set_title('Frequency Domain (Welch\'s Method)')
    ax2.set_xlabel('Frequency (Hz)')
    ax2.set_ylabel('Power Spectral Density (V²/Hz)')
    ax2.legend()
    ax2.grid(True)
    
    # Add main title
    fig.suptitle(title, fontsize=14)
    
    # Enable interactive features
    plt.rcParams['toolbar'] = 'toolmanager'
    fig.canvas.manager.set_window_title('Interactive Signal Viewer')
    
    # Adjust layout
    plt.tight_layout()
    
    return fig

def test_filtering(input_file: str, output_file: str):
    """
    Test filtering results by comparing original and filtered signals from a processed file.
    
    Args:
        input_file (str): Path to the processed data file
        output_file (str): Path to save the comparison plot
    """
    # Load the processed data
    data = load_data(input_file)
    
    # Get metadata
    metadata = data['subject_metadata']
    sampling_rate = metadata['sampling_rate']
    subject_name = metadata['subject_name']
    filter_band = metadata.get('filter_band')
    
    if not filter_band:
        raise ValueError("No filter band found in the processed data")
    
    # Randomly select a sample
    sample_names = list(data['samples'].keys())
    if not sample_names:
        raise ValueError("No samples found in the processed data")
    sample_name = random.choice(sample_names)
    print(f"Selected sample: {sample_name}")
    
    sample_data = data['samples'][sample_name]
    
    # Get original and filtered signals
    original_signal = np.array(sample_data['signal_mv'], dtype=float)
    filtered_signal = np.array(sample_data['filtered_signal'], dtype=float)
    
    print(f"Original signal shape: {original_signal.shape}")
    print(f"Filtered signal shape: {filtered_signal.shape}")
    
    if filtered_signal is None:
        raise ValueError("No filtered signal found in the processed data")
    
    # Create plot title
    title = f"Signal Comparison - {subject_name} - {sample_name}"
    title += f" (Filtered: {filter_band[0]}-{filter_band[1]} Hz)"
    
    # Create the interactive plot
    fig = plot_signal_comparison(original_signal, filtered_signal, sampling_rate, 
                               filter_band, title)
    
    # Save the plot
    fig.savefig(output_file)
    
    # Show the interactive plot
    plt.show()
    
    print(f"Plot saved to: {output_file}")