import re
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
import json
from scipy import signal
import random
from typing import Optional, Tuple


def load_data(file_path: str) -> dict:
    """Load data from a JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)

def extract_filter_band_from_filename(filename: str) -> Optional[Tuple[int, int]]:
    """
    Extract filter band from filename.
    Expected format: subject_processed_LOW-HIGHHz.json
    
    Args:
        filename (str): Name of the processed file
        
    Returns:
        Optional[Tuple[int, int]]: (low_freq, high_freq) or None if no filter band found
    """
    match = re.search(r'_(\d+)-(\d+)Hz\.json$', filename)
    if match:
        return (int(match.group(1)), int(match.group(2)))
    return None

def create_time_domain_plot(original_signal: np.ndarray, 
                            filtered_signal: np.ndarray, 
                            sampling_rate: float, 
                            title: str = "Time Domain") -> go.Figure:
    """
    Creates a Plotly figure for the time domain representation of signals.

    Args:
        original_signal (np.ndarray): The original signal in millivolts.
        filtered_signal (np.ndarray): The filtered signal in millivolts.
        sampling_rate (float): The sampling rate of the signals in Hz.
        title (str): The title of the plot.

    Returns:
        go.Figure: A Plotly figure object.
    """
    original_signal = np.asarray(original_signal, dtype=float).flatten()
    filtered_signal = np.asarray(filtered_signal, dtype=float).flatten()
    
    if len(original_signal) != len(filtered_signal):
        raise ValueError("Signal lengths must match.")
    if len(original_signal) < 1:
        raise ValueError("Signals cannot be empty.")

    time_axis = np.arange(len(original_signal)) / sampling_rate

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=time_axis, y=original_signal, mode='lines', name='Original (mV)', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=time_axis, y=filtered_signal, mode='lines', name='Filtered (mV)', line=dict(color='red')))

    fig.update_layout(
        title=title,
        xaxis_title="Time (s)",
        yaxis_title="Amplitude (mV)",
        legend_title="Signals"
    )
    return fig

def create_frequency_domain_plot(original_signal: np.ndarray, 
                                 filtered_signal: np.ndarray, 
                                 sampling_rate: float, 
                                 title: str = "Frequency Domain (Power Spectral Density)",
                                 y_axis_type: str = 'log',
                                 filter_band_processed: Optional[Tuple[float, float]] = None) -> go.Figure:
    """
    Creates a Plotly figure for the frequency domain (PSD) representation of signals.

    Args:
        original_signal (np.ndarray): The original signal in millivolts.
        filtered_signal (np.ndarray): The filtered signal in millivolts.
        sampling_rate (float): The sampling rate of the signals in Hz.
        title (str): The title of the plot.
        y_axis_type (str): Type of y-axis ('log' or 'linear'). Defaults to 'log'.
        filter_band_processed (Optional[Tuple[float, float]]): Tuple of (low_freq, high_freq) from processing, for visualization.

    Returns:
        go.Figure: A Plotly figure object.
    """
    original_signal = np.asarray(original_signal, dtype=float).flatten()
    filtered_signal = np.asarray(filtered_signal, dtype=float).flatten()

    if len(original_signal) < 8: # Welch method needs enough points
        raise ValueError("Signal too short for Welch method. Minimum 8 points required.")

    # Compute PSD using Welch's method
    nperseg = min(256, len(original_signal) // 2 if len(original_signal) >=8 else len(original_signal)) # Ensure nperseg is not too large for short signals
    
    freqs_orig, psd_orig = signal.welch(original_signal, sampling_rate, nperseg=nperseg)
    freqs_filt, psd_filt = signal.welch(filtered_signal, sampling_rate, nperseg=nperseg)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=freqs_orig, y=psd_orig, mode='lines', name='Original PSD', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=freqs_filt, y=psd_filt, mode='lines', name='Filtered PSD', line=dict(color='red')))
    
    if filter_band_processed:
        low_freq, high_freq = filter_band_processed
        fig.add_vrect(
            x0=low_freq, x1=high_freq,
            fillcolor="green", opacity=0.2,
            layer="below", line_width=0,
            name=f"Filter Band ({low_freq}-{high_freq} Hz)"
        )


    fig.update_layout(
        title=title,
        xaxis_title="Frequency (Hz)",
        yaxis_title="Power Spectral Density (mV²/Hz)",
        yaxis_type=y_axis_type,
        legend_title="PSD"
    )
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
    # The line below refers to a function that no longer exists in this file (plot_signal_comparison)
    # and was previously using PyQtGraph. This whole test_filtering function is likely vestigial
    # as the Streamlit app test_filtering.py now handles this logic.
    # For now, I'll comment it out to prevent errors if this function were somehow called.
    # win = plot_signal_comparison(original_signal, filtered_signal, sampling_rate, 
    #                            filter_band, title)
    
    # Save the plot
    # win.export(output_file) # This would also error as 'win' is not defined
    
    # Start Qt event loop
    # pg.exec() # pg is no longer imported
    
    print(f"Plot saved to: {output_file} (Note: Plot generation in this function is currently commented out)")