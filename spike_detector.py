import numpy as np
import json

class SpikeDetector:
    def __init__(self, subject_data_dict):
        """
        Initializes the SpikeDetector with data for a single subject.

        Args:
            subject_data_dict (dict): The Python dictionary loaded from a
                                      <subject_name>_processed.json file.
        """
        if not isinstance(subject_data_dict, dict):
            raise ValueError("subject_data_dict must be a dictionary.")
        self.data = subject_data_dict
        self.sampling_rate = self.data.get("subject_metadata", {}).get("sampling_rate")
        if self.sampling_rate is None:
            raise ValueError("Sampling rate not found in subject metadata.")

    # _find_peak_in_segment can be removed if peak finding is simplified within detect_spikes_in_signal
    # or kept if it's generic enough. For RMS, we care about abs value for threshold, then actual peak.

    def detect_spikes_in_signal(self, signal, n_rms_multiplier=4):
        """
        Detects spikes in a single signal array using RMS-based thresholding.
        Only detects negative spikes (values below -n_rms_multiplier * RMS).

        Args:
            signal (np.array): The signal to analyze (e.g., filtered_signal or signal_mv).
            n_rms_multiplier (float): The multiplier for RMS to set the threshold.

        Returns:
            dict: A dictionary with two keys: 'raw_detected' (spikes before refractory filter) and 'refractory_filtered' (spikes after filter).
        """
        if not isinstance(signal, np.ndarray):
            signal = np.array(signal)
        if signal.size == 0:  # handles empty list, empty array
            return {"raw_detected": [], "refractory_filtered": []}
        # Ensure signal is at least 1D (it would be 0D if input was a scalar that became a 0D array)
        if signal.ndim == 0:
            signal = signal.reshape(1)  # Convert 0D scalar array to 1D array with one element
        
        # Ensure signal is strictly 1D (e.g., flatten if it was (N,1) or (1,N))
        if signal.ndim > 1:
            signal = signal.ravel()

        rms_signal = np.sqrt(np.mean(signal**2))

        if rms_signal == 0:  # Avoid issues if signal is all zeros
            return {"raw_detected": [], "refractory_filtered": []}

        threshold_value = -n_rms_multiplier * rms_signal  # Negative threshold

        # Identify points where the signal crosses the negative threshold
        supra_threshold_mask = signal < threshold_value
        
        detected_spikes = []
        if not np.any(supra_threshold_mask):
            return {"raw_detected": [], "refractory_filtered": []}

        # Find contiguous segments of supra-threshold points
        # Add a value at the beginning and end to make diff work for edges
        diff_mask = np.diff(np.concatenate(([False], supra_threshold_mask, [False])).astype(int))
        
        segment_starts = np.where(diff_mask == 1)[0]
        # end_idx from diff is exclusive for slicing, so segment_ends[i] is the first index *after* the segment
        segment_ends = np.where(diff_mask == -1)[0]

        for start_idx, end_idx in zip(segment_starts, segment_ends):
            segment_values = signal[start_idx:end_idx]  # Contains all values in the segment
            segment_indices = np.arange(start_idx, end_idx)  # Original indices for these values

            if segment_values.size == 0:
                continue

            # Find the minimum value (most negative) within this segment
            peak_idx_in_segment = np.argmin(segment_values)
            
            peak_amplitude = segment_values[peak_idx_in_segment]
            peak_original_idx = segment_indices[peak_idx_in_segment]
            
            spike_time_s = peak_original_idx / self.sampling_rate
            detected_spikes.append({
                "time_s": spike_time_s,
                "amplitude_mv": peak_amplitude,
                "index": int(peak_original_idx)
            })
        
        # Sort detected spikes by time
        detected_spikes.sort(key=lambda x: x["time_s"])
        raw_detected_spikes = list(detected_spikes)  # Store a copy of raw detections

        # Define refractory/window parameters
        ref_before_s = 0.001  # 1 ms
        ref_after_s = 0.002   # 2 ms
        
        refractory_filtered_spikes = self._filter_spikes_iterative_refractory(raw_detected_spikes, ref_before_s, ref_after_s)
        
        return {
            "raw_detected": raw_detected_spikes,
            "refractory_filtered": refractory_filtered_spikes
        }

    def _filter_spikes_iterative_refractory(self, initial_spikes_sorted, before_s, after_s):
        """
        Filters spikes based on an iterative refractory period.
        Spikes are processed in time order. A spike is kept if its peak does not fall
        into the event window [P_j - before_s, P_j + after_s] of any *previously validated* spike S_j.
        If a spike is kept, its own event window is then used for checking subsequent spikes.

        Args:
            initial_spikes_sorted (list): List of initially detected spike dictionaries,
                                          MUST BE SORTED by "time_s".
            before_s (float): Time in seconds for window start (Peak - before_s).
            after_s (float): Time in seconds for window end (Peak + after_s).

        Returns:
            list: A new list of validated spike dictionaries.
        """
        if not initial_spikes_sorted:
            return []

        validated_spikes = []
        active_windows = [] # List of [window_start, window_end] for validated spikes

        for current_spike in initial_spikes_sorted:
            current_peak_time = current_spike["time_s"]
            is_shadowed_by_active_window = False

            # Check against windows of previously validated spikes
            for window_start, window_end in active_windows:
                if window_start <= current_peak_time <= window_end:
                    is_shadowed_by_active_window = True
                    break 
            
            if not is_shadowed_by_active_window:
                validated_spikes.append(current_spike)
                # Add this validated spike's window to active_windows for future checks
                new_window_start = current_peak_time - before_s
                new_window_end = current_peak_time + after_s
                active_windows.append([new_window_start, new_window_end])
                # Optimization: Prune active_windows if it becomes too large.
                # For example, remove windows whose window_end is much smaller than current_peak_time.
                # This is only necessary if performance becomes an issue on very long spike trains.
                # A simple pruning strategy:
                # active_windows = [w for w in active_windows if w[1] >= current_peak_time - (before_s + after_s + some_buffer)]

        return validated_spikes

    def process_all_samples(self, n_rms_multiplier=4):
        """
        Processes all samples in the loaded subject data to detect spikes.
        Modifies the self.data dictionary in place by adding:
        - "spikes_raw_detected": All detected spikes
        - "spikes_refractory_filtered": Filtered spikes with their waveforms
        - "spike_waveform_metadata": Information about waveform extraction parameters

        Args:
            n_rms_multiplier (float): The RMS multiplier for the threshold.
        """
        if "samples" not in self.data or not isinstance(self.data["samples"], dict):
            print("Warning: No samples found or samples format is incorrect.")
            return self.data # Return original data if no samples

        # Add waveform extraction parameters to metadata
        if "subject_metadata" in self.data:
            self.data["subject_metadata"]["spike_waveform_params"] = {
                "before_ms": 2.0,  # Time before spike peak
                "after_ms": 3.0    # Time after spike peak
            }

        for sample_name, sample_data in self.data["samples"].items():
            signal_to_process = None
            # Prioritize filtered_signal if available and not empty
            if "filtered_signal" in sample_data and \
               sample_data["filtered_signal"] is not None and \
               len(sample_data["filtered_signal"]) > 0:
                signal_to_process = np.array(sample_data["filtered_signal"])
            # Fallback to signal_mv if filtered_signal is not suitable
            elif "signal_mv" in sample_data and \
                 sample_data["signal_mv"] is not None and \
                 len(sample_data["signal_mv"]) > 0:
                signal_to_process = np.array(sample_data["signal_mv"])
            
            if signal_to_process is not None and signal_to_process.size > 0:
                if self.sampling_rate is None or self.sampling_rate <= 0:
                    print(f"Warning: Invalid sampling rate ({self.sampling_rate}) for sample {sample_name}. Skipping spike detection.")
                    sample_data["spikes_raw_detected"] = []
                    sample_data["spikes_refractory_filtered"] = []
                    continue

                # Detect spikes
                spike_detection_results = self.detect_spikes_in_signal(
                    signal_to_process, 
                    n_rms_multiplier=n_rms_multiplier
                )
                
                # Extract waveforms for refractory-filtered spikes
                waveforms_data = self.extract_spike_waveforms(
                    signal=signal_to_process,
                    spike_times_list=spike_detection_results["refractory_filtered"],
                    before_ms=2,
                    after_ms=3
                )

                # Add waveforms to each spike in refractory_filtered
                refractory_filtered_with_waveforms = []
                for i, spike in enumerate(spike_detection_results["refractory_filtered"]):
                    if spike["index"] in waveforms_data["spike_indices"]:
                        # Find the index of this spike in the waveforms data
                        waveform_idx = waveforms_data["spike_indices"].index(spike["index"])
                        spike_with_waveform = spike.copy()
                        spike_with_waveform["waveform"] = waveforms_data["waveforms"][waveform_idx].tolist()
                        refractory_filtered_with_waveforms.append(spike_with_waveform)
                    else:
                        # If for some reason we couldn't extract the waveform, still keep the spike
                        refractory_filtered_with_waveforms.append(spike)

                # Store results
                sample_data["spikes_raw_detected"] = spike_detection_results["raw_detected"]
                sample_data["spikes_refractory_filtered"] = refractory_filtered_with_waveforms
                sample_data["spike_waveform_metadata"] = {
                    "time_axis_ms": waveforms_data["time_axis"].tolist(),
                    "before_ms": 2.0,
                    "after_ms": 3.0
                }
            else:
                sample_data["spikes_raw_detected"] = []
                sample_data["spikes_refractory_filtered"] = []
                sample_data["spike_waveform_metadata"] = None
        
        return self.data

    def _filter_spikes_by_separation(self, spikes, refractory_before_s, refractory_after_s):
        """
        Filters a list of spikes to ensure minimum time separation.
        A spike is kept if its time minus the time of the previously kept spike
        is greater than (refractory_before_s + refractory_after_s).
        This ensures that the current spike's "before" window does not start
        until after the previous spike's "after" window has ended.

        Args:
            spikes (list): List of spike dictionaries, MUST BE SORTED by "time_s".
            refractory_before_s (float): The "clear before" time in seconds required for a spike.
            refractory_after_s (float): The "clear after" time in seconds imposed by a spike.

        Returns:
            list: A new list of spike dictionaries respecting the separation.
        """
        if not spikes:
            return []

        # The effective minimum time gap needed between the peak of the last accepted spike
        # and the peak of the current candidate spike.
        min_separation_s = refractory_before_s + refractory_after_s # Sum of durations

        validated_spikes = [spikes[0]] # First spike is always accepted
        last_accepted_time = spikes[0]["time_s"]

        for current_spike in spikes[1:]:
            if (current_spike["time_s"] - last_accepted_time) > min_separation_s:
                validated_spikes.append(current_spike)
                last_accepted_time = current_spike["time_s"]
        
        return validated_spikes

    def extract_spike_waveforms(self, signal, spike_times_list, before_ms=2, after_ms=3):
        """
        Extracts spike waveforms from the signal based on spike times.
        
        Args:
            signal (np.ndarray): The signal to extract waveforms from (typically filtered_signal)
            spike_times_list (list): List of dictionaries containing spike information with 'time_s' field
            before_ms (float): Time in milliseconds to extract before the spike peak (default: 2)
            after_ms (float): Time in milliseconds to extract after the spike peak (default: 3)
            
        Returns:
            dict: A dictionary containing:
                - 'waveforms': List of extracted waveforms as numpy arrays
                - 'time_axis': Time axis for the waveforms in milliseconds
                - 'spike_indices': Original indices of successfully extracted waveforms
        """
        if not isinstance(signal, np.ndarray):
            signal = np.array(signal)
        
        # Ensure signal is 1D
        signal = signal.ravel()
        signal_length = signal.size
        
        # Convert ms to samples
        samples_before = int(before_ms * self.sampling_rate / 1000)
        samples_after = int(after_ms * self.sampling_rate / 1000)
        waveform_length = samples_before + samples_after + 1  # +1 for the peak sample
        
        # Initialize lists to store results
        waveforms = []
        valid_spike_indices = []
        
        # Create time axis in milliseconds for the waveforms
        time_axis = np.arange(-samples_before, samples_after + 1) * 1000 / self.sampling_rate
        
        for spike in spike_times_list:
            spike_idx = spike['index']
            
            # Check if we can extract the full waveform
            if spike_idx >= samples_before and spike_idx + samples_after < signal_length:
                # Extract waveform
                waveform = signal[spike_idx - samples_before : spike_idx + samples_after + 1]
                waveforms.append(waveform)
                valid_spike_indices.append(spike_idx)
        
        return {
            'waveforms': np.array(waveforms) if waveforms else np.array([]),
            'time_axis': time_axis,
            'spike_indices': valid_spike_indices
        }

# Example Usage (for testing, typically run from another script):
# if __name__ == '__main__':
#     # This part would be in your main processing script for spike detection
#     processed_file_path = "path_to_your_subject_processed.json"
#     output_spikes_file_path = "path_to_your_subject_spikes_detected.json"
#     n_rms = 4

#     try:
#         with open(processed_file_path, 'r') as f:
#             data_dict = json.load(f)
#     except FileNotFoundError:
#         print(f"Error: Processed JSON file not found at {processed_file_path}")
#         exit()
#     except json.JSONDecodeError:
#         print(f"Error: Could not decode JSON file from {processed_file_path}")
#         exit()

#     if "subject_metadata" not in data_dict or "sampling_rate" not in data_dict["subject_metadata"]:
#         print("Error: 'sampling_rate' not found in subject_metadata of the loaded file.")
#         # Handle error appropriately, e.g., skip this file or use a default
#         exit()

#     spike_detector = SpikeDetector(data_dict)
    
#     modified_data_with_spikes = spike_detector.process_all_samples(n_rms_multiplier=n_rms)

#     try:
#         with open(output_spikes_file_path, 'w') as f:
#             json.dump(modified_data_with_spikes, f, indent=4)
#         print(f"Successfully processed and saved data with spikes to {output_spikes_file_path}")
#     except IOError:
#         print(f"Error: Could not write spikes detected JSON file to {output_spikes_file_path}") 