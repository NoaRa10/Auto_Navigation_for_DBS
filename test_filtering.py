import streamlit as st
import numpy as np
import json
import random
from pathlib import Path
import re # For extracting subject names
from test_filter_helper_func import (
    load_data,
    create_time_domain_plot,
    create_frequency_domain_plot
)

st.set_page_config(layout="wide")

st.title("Signal Filtering Test Dashboard")

# --- Session State Initialization ---
if 'y_axis_type' not in st.session_state:
    st.session_state.y_axis_type = 'log'
if 'selected_subject' not in st.session_state:
    st.session_state.selected_subject = None
if 'selected_file_name' not in st.session_state:
    st.session_state.selected_file_name = None

# --- File and Subject Selection Logic ---
st.sidebar.header("Data File Selection")

processed_data_dir = Path("processed_data")
if not processed_data_dir.exists():
    st.sidebar.error(f"Directory not found: {processed_data_dir}")
    st.stop()

all_processed_files = [f.name for f in processed_data_dir.glob("*_processed_*.json")]

if not all_processed_files:
    st.sidebar.warning(f"No processed JSON files found in {processed_data_dir}.")
    st.sidebar.markdown("Please ensure your processed files (e.g., `Subject_X_processed_LOW-HIGHHz.json`) are in this directory.")
    st.stop()

# Extract unique subject names
subject_names = sorted(list(set([re.match(r"^(Subject_\d+)_.*", f).group(1) 
                                for f in all_processed_files 
                                if re.match(r"^(Subject_\d+)_.*", f)])))

if not subject_names:
    st.sidebar.error("Could not extract subject names from the files. Ensure filenames start with 'Subject_X_'.")
    st.stop()

# 1. Select Subject
selected_subject = st.sidebar.selectbox(
    "Choose a Subject:",
    subject_names,
    index=subject_names.index(st.session_state.selected_subject) if st.session_state.selected_subject in subject_names else 0
)
st.session_state.selected_subject = selected_subject

# 2. Filter files for the selected subject and then select a file
files_for_subject = sorted([f for f in all_processed_files if f.startswith(selected_subject)])

if not files_for_subject:
    st.sidebar.error(f"No processed files found for {selected_subject}.")
    st.stop()

selected_file_name = st.sidebar.selectbox(
    f"Choose a file for {selected_subject}:",
    files_for_subject,
    index=files_for_subject.index(st.session_state.selected_file_name) if st.session_state.selected_file_name in files_for_subject else 0
)
st.session_state.selected_file_name = selected_file_name

input_file_path = processed_data_dir / selected_file_name

if not input_file_path.exists():
    st.error(f"Something went wrong. Selected file not found: {input_file_path}")
    st.stop()

# --- Data Loading and Processing Logic ---
st.header(f"Visualizing: {selected_subject} - File: {selected_file_name}")

try:
    data = load_data(str(input_file_path))
except Exception as e:
    st.error(f"Error loading data from {input_file_path}: {e}")
    st.stop()

metadata = data.get('subject_metadata')
if not metadata:
    st.error("Subject metadata not found in the file.")
    st.stop()

sampling_rate = metadata.get('sampling_rate')
# subject_name_from_metadata = metadata.get('subject_name', "N/A") # We use selected_subject now
filter_band_from_metadata = metadata.get('filter_band')

if sampling_rate is None:
    st.error("Sampling rate not found in metadata.")
    st.stop()

samples = data.get('samples')
if not samples:
    st.error("No samples found in the data.")
    st.stop()

sample_names_in_file = list(samples.keys())

st.sidebar.header("Sample Selection in File")
if len(sample_names_in_file) > 1:
    selected_sample_key = st.sidebar.selectbox(
        f"Choose a sample from '{selected_file_name}':", 
        sample_names_in_file, 
        index=0
    )
else:
    selected_sample_key = sample_names_in_file[0]
    st.sidebar.write(f"Displaying sample: {selected_sample_key}")

sample_data = samples[selected_sample_key]

original_signal_mv = np.array(sample_data.get('signal_mv', []))
filtered_signal = np.array(sample_data.get('filtered_signal', []))

if original_signal_mv.size == 0 or filtered_signal.size == 0:
    st.error(f"Signal data (signal_mv or filtered_signal) is missing or empty for sample '{selected_sample_key}'.")
    st.stop()

# --- Plotting --- 
if filter_band_from_metadata:
    st.subheader(f"Data in file processed with filter: {filter_band_from_metadata[0]}-{filter_band_from_metadata[1]} Hz")
else:
    st.subheader("Filter band from metadata not specified.")

# Time Domain Plot
time_plot_title = f"Time Domain: {selected_subject} - Sample {selected_sample_key}"
st.plotly_chart(create_time_domain_plot(original_signal_mv, filtered_signal, sampling_rate, title=time_plot_title), use_container_width=True)

# Frequency Domain Plot
st.subheader("Frequency Domain Analysis")

if st.button("Toggle Frequency Plot Y-Axis (Log/Linear)"):
    st.session_state.y_axis_type = 'linear' if st.session_state.y_axis_type == 'log' else 'log'

freq_plot_title = f"Frequency Domain (PSD): {selected_subject} - Sample {selected_sample_key}"
st.plotly_chart(create_frequency_domain_plot(
    original_signal_mv, 
    filtered_signal, 
    sampling_rate, 
    title=freq_plot_title,
    y_axis_type=st.session_state.y_axis_type,
    filter_band_processed=filter_band_from_metadata
), use_container_width=True)

st.sidebar.markdown("--- ")
st.sidebar.markdown("**How to use:**")
st.sidebar.markdown("1. Select a Subject.")
st.sidebar.markdown("2. Select a specific processed file for that subject.")
st.sidebar.markdown("3. If multiple samples exist in the file, select one.")
st.sidebar.markdown("4. Use the button to toggle the frequency plot's Y-axis scale.")

# To run this app: streamlit run test_filtering.py 