import streamlit as st
import numpy as np
import json
from pathlib import Path
import re

# Import the new main plotting function from the helper file
from spikes_visualization_helper_func import create_combined_visualization, load_data

st.set_page_config(layout="wide")
st.title("Spike Visualization Dashboard")

# --- Session State Initialization ---
if 'selected_subject' not in st.session_state:
    st.session_state.selected_subject = None
if 'selected_file_name' not in st.session_state:
    st.session_state.selected_file_name = None

# --- File and Subject Selection Logic ---
st.sidebar.header("Data File Selection")
processed_data_dir = Path("spikes_data") 

if not processed_data_dir.exists():
    st.sidebar.error(f"Directory not found: {processed_data_dir}")
    st.error(f"Directory '{processed_data_dir}' not found. Please create it and add your data files.")
    st.stop()

all_input_files = [f.name for f in processed_data_dir.glob("*.json")] 

if not all_input_files:
    st.sidebar.warning(f"No JSON files found in {processed_data_dir}.")
    st.info(f"No JSON files found in '{processed_data_dir}'. Please add data files for spike detection.")
    st.stop()

subject_names = sorted(list(set([re.match(r"^(Subject_[^_]+)_.*", f).group(1)
                                for f in all_input_files
                                if re.match(r"^(Subject_[^_]+)_.*", f)])))

if not subject_names:
    st.sidebar.error("Could not extract subject names. Ensure filenames start with 'Subject_X_' (X can be any char not '_').")
    st.error(f"Could not extract subject names from files in '{processed_data_dir}'. Ensure filenames follow the pattern 'Subject_X_...'.")
    st.stop()

selected_subject_option = st.sidebar.selectbox(
    "Choose a Subject:",
    ["Select a Subject"] + subject_names,
    index=0
)

if selected_subject_option == "Select a Subject":
    st.info("Please select a subject from the sidebar.")
    st.stop()
st.session_state.selected_subject = selected_subject_option

files_for_subject = sorted([f for f in all_input_files if f.startswith(st.session_state.selected_subject)])

if not files_for_subject:
    st.sidebar.error(f"No files found for {st.session_state.selected_subject}.")
    st.error(f"No files found for {st.session_state.selected_subject} in '{processed_data_dir}'. Check subject or file patterns.")
    st.stop()

default_file_index = 0
if st.session_state.selected_file_name in files_for_subject:
    default_file_index = files_for_subject.index(st.session_state.selected_file_name)

selected_file_name_option = st.sidebar.selectbox(
    f"Choose a file for {st.session_state.selected_subject}:",
    files_for_subject,
    index=default_file_index
)

if selected_file_name_option is None:
    st.error(f"CRITICAL ERROR: File selection returned None for subject '{st.session_state.selected_subject}'. Files available: {files_for_subject}")
    st.stop()
st.session_state.selected_file_name = selected_file_name_option
input_file_path = processed_data_dir / selected_file_name_option

if not input_file_path.exists():
    st.error(f"Selected file not found: {input_file_path}")
    st.stop()

st.header(f"Visualizing: {st.session_state.selected_subject} - File: {st.session_state.selected_file_name}")

# Load the processed data with spikes
data = load_data(str(input_file_path))

metadata = data.get('subject_metadata')
if not metadata:
    st.error("Subject metadata not found in the processed file.")
    st.stop()

sampling_rate = metadata.get('sampling_rate')
if sampling_rate is None:
    st.error("Sampling rate not found in metadata.")
    st.stop()

filter_band_from_metadata = metadata.get('filter_band')

samples_dict = data.get('samples')
if not samples_dict:
    st.error("No samples found in the processed data.")
    st.stop()

sample_names_in_file = list(samples_dict.keys())
st.sidebar.header("Sample Selection in File")
selected_sample_key = ""
if len(sample_names_in_file) > 1:
    selected_sample_key = st.sidebar.selectbox(
        f"Choose a sample from '{st.session_state.selected_file_name}':", 
        sample_names_in_file, 
        index=0
    )
elif sample_names_in_file:
    selected_sample_key = sample_names_in_file[0]
    st.sidebar.write(f"Displaying sample: {selected_sample_key}")
else:
    st.error("No sample keys found in the 'samples' dictionary.")
    st.stop()

current_sample_data = samples_dict[selected_sample_key]
filtered_signal = np.array(current_sample_data.get('filtered_signal', current_sample_data.get('signal_mv', [])))

if filtered_signal.size == 0:
    st.error(f"Signal data ('filtered_signal' or 'signal_mv') is missing or empty for sample '{selected_sample_key}'.")
    st.stop()

# Extract spike times and waveforms
raw_spikes_list = current_sample_data.get('spikes_raw_detected', [])
filtered_spikes_list = current_sample_data.get('spikes_refractory_filtered', [])

raw_spike_times = [spike['time_s'] for spike in raw_spikes_list if isinstance(spike, dict) and 'time_s' in spike]
filtered_spike_times = [spike['time_s'] for spike in filtered_spikes_list if isinstance(spike, dict) and 'time_s' in spike]

# Extract waveforms and time axis
waveforms = None
time_axis_ms = None
if filtered_spikes_list and 'waveform' in filtered_spikes_list[0]:
    waveforms = np.array([spike['waveform'] for spike in filtered_spikes_list if 'waveform' in spike])
    waveform_metadata = current_sample_data.get('spike_waveform_metadata', {})
    time_axis_ms = waveform_metadata.get('time_axis_ms')

if filter_band_from_metadata:
    st.subheader(f"Data in file (filter: {filter_band_from_metadata[0]}-{filter_band_from_metadata[1]} Hz if applied before spike detection)")
else:
    st.subheader("Filter band from original metadata not specified.")

# Create the visualization
fig = create_combined_visualization(
    filtered_signal=filtered_signal,
    sampling_rate=sampling_rate,
    raw_spike_times=raw_spike_times,
    filtered_spike_times=filtered_spike_times,
    waveforms=waveforms,
    time_axis_ms=time_axis_ms,
    signal_title=f"{st.session_state.selected_subject} - Sample {selected_sample_key} - Filtered Signal",
    raster_title="Spike Raster",
    waveform_title="Spike Waveforms",
    spike_times_for_waveforms=filtered_spike_times
)

# Display the figure
st.plotly_chart(fig, use_container_width=True)

# Display spike counts
st.write(f"Number of raw spikes detected: {len(raw_spike_times)}")
st.write(f"Number of refractory-filtered spikes: {len(filtered_spike_times)}")
if waveforms is not None:
    st.write(f"Number of extracted waveforms: {len(waveforms)}")

st.sidebar.markdown("---")
st.sidebar.markdown("**How to use:**")
st.sidebar.markdown("1. Ensure JSON files are in the `spikes_data` directory.")
st.sidebar.markdown("2. Select a Subject, File, and Sample.")
st.sidebar.markdown("3. View the filtered signal, spike waveforms, and raster plots.")

# To run this app: streamlit run spikes_visualizer.py 