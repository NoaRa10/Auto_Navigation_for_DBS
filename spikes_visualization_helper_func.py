import re
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
import json
from scipy import signal
import random
from typing import Optional, Tuple, List


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

def create_time_domain_plot(
    filtered_signal: np.ndarray, 
    sampling_rate: float, 
    title: str = "Filtered Signal"
) -> go.Figure:
    """Creates a Plotly figure for the time domain representation of the filtered signal."""
    filtered_signal_flat = np.asarray(filtered_signal, dtype=float).flatten()
    fig = go.Figure()

    if len(filtered_signal_flat) < 1:
        fig.update_layout(title_text=f"{title} (No signal data)")
        return fig # Return an empty figure with a title

    time_axis_signal = np.arange(len(filtered_signal_flat)) / sampling_rate
    fig.add_trace(go.Scatter(
        x=time_axis_signal, 
        y=filtered_signal_flat, 
        mode='lines', 
        name='Filtered Signal',
        line=dict(color='blue')
    ))
    
    min_val = np.min(filtered_signal_flat)
    max_val = np.max(filtered_signal_flat)
    padding = (max_val - min_val) * 0.05
    padding = padding if padding > 0 else np.abs(min_val * 0.05) if min_val != 0 else 0.1
    
    fig.update_layout(
        title_text=title,
        xaxis_title="Time (s)",
        yaxis_title="Amplitude (mV)",
        showlegend=False # Single trace plot, legend not essential
    )
    fig.update_yaxes(range=[min_val - padding, max_val + padding])
    return fig

def create_spike_raster_plot(
    raw_spike_times: List[float],
    filtered_spike_times: List[float],
    title: str = "Spike Raster"
) -> go.Figure:
    """Creates a Plotly figure for the spike raster plot."""
    fig = go.Figure()

    if not raw_spike_times and not filtered_spike_times:
        fig.update_layout(title_text=f"{title} (No spike data)")
        return fig # Return an empty figure with a title

    if raw_spike_times:
        fig.add_trace(go.Scatter(
            x=raw_spike_times,
            y=np.ones(len(raw_spike_times)) * 1,
            mode='markers',
            name='Raw Spikes',
            marker=dict(color='red', symbol='line-ns', size=10, line=dict(width=1.5)),
        ))

    if filtered_spike_times:
        fig.add_trace(go.Scatter(
            x=filtered_spike_times,
            y=np.ones(len(filtered_spike_times)) * 1.2,
            mode='markers',
            name='Filtered Spikes',
            marker=dict(color='green', symbol='line-ns', size=10, line=dict(width=1.5)),
        ))
    
    fig.update_layout(
        title_text=title,
        xaxis_title="Time (s)",
        yaxis_title="Spikes",
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig.update_yaxes(
        showticklabels=False, 
        range=[0.8, 1.4],
        zeroline=False
    )
    return fig

def create_signal_and_raster_figure(
    filtered_signal: np.ndarray,
    sampling_rate: float,
    raw_spike_times: List[float],
    filtered_spike_times: List[float],
    signal_title: str = "Filtered Signal",
    raster_title: str = "Spike Raster",
    figure_height: int = 700
) -> go.Figure:
    """Combines the signal plot and spike raster plot into a single figure with shared x-axes."""
    
    combined_fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.7, 0.3],
        subplot_titles=(signal_title, raster_title)
    )

    # --- Subplot 1: Filtered Signal ---
    if filtered_signal.size > 0:
        filtered_signal_flat = np.asarray(filtered_signal, dtype=float).flatten()
        time_axis_signal = np.arange(len(filtered_signal_flat)) / sampling_rate
        
        combined_fig.add_trace(go.Scatter(
            x=time_axis_signal, 
            y=filtered_signal_flat, 
            mode='lines', 
            name='Filtered Signal',
            line=dict(color='blue'),
            showlegend=False
        ), row=1, col=1)
        
        # More robust y-axis scaling
        min_val = np.min(filtered_signal_flat)
        max_val = np.max(filtered_signal_flat)
        value_range = max_val - min_val
        if value_range == 0:  # Handle constant signal
            padding = np.abs(min_val * 0.1) if min_val != 0 else 0.1
        else:
            padding = value_range * 0.1
        
        combined_fig.update_yaxes(
            title_text="Amplitude (mV)", 
            range=[min_val - padding, max_val + padding],
            row=1, col=1
        )
    else:
        combined_fig.add_annotation(
            text="No signal data", 
            xref="paper", 
            yref="paper", 
            x=0.5, 
            y=0.85, 
            showarrow=False, 
            row=1, col=1
        )
        combined_fig.update_yaxes(title_text="Amplitude (mV)", row=1, col=1)

    # --- Subplot 2: Spike Raster ---
    if raw_spike_times:
        combined_fig.add_trace(go.Scatter(
            x=raw_spike_times,
            y=np.ones(len(raw_spike_times)),  # All spikes at y=1
            mode='markers',
            name='Raw Spikes',
            marker=dict(
                color='red',
                symbol='line-ns',
                size=12,
                line=dict(width=1, color='red')
            )
        ), row=2, col=1)

    if filtered_spike_times:
        combined_fig.add_trace(go.Scatter(
            x=filtered_spike_times,
            y=np.ones(len(filtered_spike_times)),  # All spikes at y=1
            mode='markers',
            name='Filtered Spikes',
            marker=dict(
                color='green',
                symbol='line-ns',
                size=12,
                line=dict(width=1, color='green')
            )
        ), row=2, col=1)
    
    if not raw_spike_times and not filtered_spike_times:
        combined_fig.add_annotation(
            text="No spike data",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.15,
            showarrow=False,
            row=2, col=1
        )

    # Configure Y-axis for raster plot
    combined_fig.update_yaxes(
        showticklabels=False, 
        title_text="Spikes", 
        range=[0.5, 1.5],  # Centered around y=1
        zeroline=False,
        row=2, col=1
    )
    
    # --- General Layout Updates ---
    combined_fig.update_xaxes(title_text="Time (s)", row=2, col=1)
    combined_fig.update_layout(
        height=figure_height,
        showlegend=True, 
        legend=dict(
            traceorder="normal",
            orientation="h",
            yanchor="top",
            y=-0.2,  # Place legend below the figure
            xanchor="center",
            x=0.5,  # Center the legend horizontally
            bgcolor="rgba(255, 255, 255, 0.9)"  # Semi-transparent white background
        ),
        margin=dict(b=80)  # Add bottom margin to accommodate the legend
    )
    
    return combined_fig