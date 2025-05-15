import os
import json
import glob
from spike_detector import SpikeDetector # Assuming spike_detector.py is in the same directory or accessible

def run_spike_detection_pipeline(input_dir, output_dir, n_rms_multiplier=4):
    """
    Loads processed data, performs spike detection, and saves the results.

    Args:
        input_dir (str): Directory containing the <subject_name>_processed.json files.
        output_dir (str): Directory where <subject_name>_spikes_detected.json files will be saved.
        n_rms_multiplier (float): The multiplier for RMS to set the spike detection threshold.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")

    # Find all processed JSON files in the input directory
    # Assuming processed files might end with _processed.json or _processed_LOW-HIGHHz.json
    search_pattern = os.path.join(input_dir, "*_processed.json")
    search_pattern_filtered = os.path.join(input_dir, "*_processed_*Hz.json")
    
    processed_files = glob.glob(search_pattern) + glob.glob(search_pattern_filtered)
    
    if not processed_files:
        print(f"No processed JSON files found in {input_dir} with patterns: {search_pattern}, {search_pattern_filtered}")
        return

    print(f"Found {len(processed_files)} processed files to analyze.")

    for file_path in processed_files:
        filename = os.path.basename(file_path)
        subject_name_base = filename.split('_processed')[0] # Get the base subject name
        
        print(f"Processing file: {filename}...")

        try:
            with open(file_path, 'r') as f:
                subject_data = json.load(f)
        except FileNotFoundError:
            print(f"Error: File not found {file_path}. Skipping.")
            continue
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from {file_path}. Skipping.")
            continue
        
        if "subject_metadata" not in subject_data or "sampling_rate" not in subject_data["subject_metadata"]:
            print(f"Error: 'sampling_rate' not found in subject_metadata for {filename}. Skipping spike detection for this file.")
            # Optionally, save the file as is to the output or handle differently
            output_filename = f"{subject_name_base}_spikes_error.json"
            output_path = os.path.join(output_dir, output_filename)
            try:
                with open(output_path, 'w') as f_out:
                    json.dump(subject_data, f_out, indent=4)
                print(f"Saved original data (due to missing sampling rate) to {output_path}")
            except IOError:
                print(f"Error: Could not write error file to {output_path}")
            continue


        # Initialize SpikeDetector
        try:
            detector = SpikeDetector(subject_data)
        except ValueError as e:
            print(f"Error initializing SpikeDetector for {filename}: {e}. Skipping.")
            continue

        # Perform spike detection
        data_with_spikes = detector.process_all_samples(n_rms_multiplier=n_rms_multiplier)

        # Add spike detection parameters to subject_metadata
        if "subject_metadata" in data_with_spikes:
            data_with_spikes["subject_metadata"]["spike_detection_params"] = {
                "method": "rms_multiplier",
                "n_rms_multiplier": float(n_rms_multiplier), # Ensure it's a float for JSON
                "refractory_period_before_s": 0.001, # Default value, consider making configurable
                "refractory_period_after_s": 0.002   # Default value, consider making configurable
            }
        else:
            # This case should ideally not happen if SpikeDetector initialized correctly
            print(f"Warning: 'subject_metadata' not found in data for {filename} before saving spike params.")

        # Determine output filename
        # Example: S01_extracted_data_processed_spikes_detected.json
        # Or, if it was S01_extracted_data_processed_1-10Hz.json -> S01_extracted_data_processed_1-10Hz_spikes_detected.json
        
        # A simpler naming: <original_base>_spikes_detected.json
        output_filename = f"{subject_name_base}_spikes_detected.json"
        if "_processed_" in filename and "Hz" in filename : # it was a filtered file
             filter_part = filename.split('_processed_')[1].split('.json')[0]
             output_filename = f"{subject_name_base}_processed_{filter_part}_spikes_detected.json"

        output_path = os.path.join(output_dir, output_filename)

        try:
            with open(output_path, 'w') as f_out:
                json.dump(data_with_spikes, f_out, indent=4)
            print(f"Successfully processed and saved spike data to {output_path}")
        except IOError:
            print(f"Error: Could not write spike data to {output_path}")
        except TypeError as e:
            print(f"Error during JSON serialization for {output_path}: {e}. Check for non-serializable types (e.g., numpy specific types if not converted).")


if __name__ == "__main__":
    # Configuration
    PROCESSED_DATA_DIR = "processed_data"  # Input directory with *_processed.json files
    SPIKES_DATA_DIR = "spikes_data"      # Output directory for *_spikes_detected.json files
    RMS_MULTIPLIER = 4                   # Threshold: 4 * RMS
    # REFRACTORY_BEFORE_S = 0.001 # Could be made a global constant or arg
    # REFRACTORY_AFTER_S = 0.002  # Could be made a global constant or arg

    print("Starting spike detection process...")
    run_spike_detection_pipeline(PROCESSED_DATA_DIR, SPIKES_DATA_DIR, RMS_MULTIPLIER)
    print("Spike detection process finished.") 