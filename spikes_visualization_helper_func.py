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

def create_time_domain_plot(filtered_signal: np.ndarray, 
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
    filtered_signal = np.asarray(filtered_signal, dtype=float).flatten()
    
    if len(filtered_signal) < 1:
        raise ValueError("Signals cannot be empty.")

    time_axis = np.arange(len(filtered_signal)) / sampling_rate

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=time_axis, y=filtered_signal, mode='lines', name='Filtered (mV)', line=dict(color='red')))

    fig.update_layout(
        title=title,
        xaxis_title="Time (s)",
        yaxis_title="Amplitude (mV)",
        legend_title="Signals"
    )
    return fig