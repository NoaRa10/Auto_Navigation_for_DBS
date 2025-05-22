# DBS Data Processor

This project processes DBS (Deep Brain Stimulation) electrophysiological data from .mat files, extracting and processing CRAW data according to specific criteria.

## Requirements

- Python 3.7 or higher
- Required packages are listed in `requirements.txt`
- MATLAB installation (R2021a or later recommended) for isolation score calculation
- ISO directory added to MATLAB path

## Installation

1. Clone this repository
2. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Ensure your data is accessible at the specified path (default: `E:\Post-Doc\DbsData\Ephys\HadassahSurgData`)
2. Run the main script:
```bash
python main.py
```

The script will:
- Process all .mat files in the subject directories
- Extract information from filenames (side, trajectory, depth, file number)
- Extract and process CRAW data from the files
- Save the processed data to `processed_data/processed_data.json`

To calculate isolation scores for detected spikes:
```bash
python run_iso_score_calculation.py
```

## Data Processing Details

The script processes files according to the following criteria:
- Only .mat files are processed
- Files must not contain "MF" in their name
- Files must contain "F" followed by 4 digits
- CRAW data is extracted and processed using bit resolution and gain values

### Spike Detection

Spikes are detected using the following criteria:
- Threshold is set at -4 * RMS of the signal (detecting negative peaks only)
- Refractory period of 1ms before and 2ms after each spike
- For each detected spike, a waveform snippet is extracted (2ms before and 3ms after the peak)
- Isolation scores are calculated to assess spike detection quality

## Output

The project generates data in several stages, with each subject's data saved in a separate JSON file.

### 1. Extracted Data (`<subject_name>_extracted.json`)

This file contains the raw signal data extracted directly from the .mat files, along with essential metadata.

```json
{
    "subject_metadata": {
        "subject_name": "S01", // Example
        "BitResolution": 1.0,  // Example
        "Gain": 25000.0,       // Example
        "KHz": 2.0             // Example (original sampling rate in KHz)
    },
    "samples": {
        "S01_L_T1_d80.5_FN1.mat": { // Key is the original .mat filename
            "raw_signal": [100, 102, 98, ...], // Raw ADC values
            "side": "L",
            "trajectory": 1,
            "depth": 80.5,
            "file_number": 1
        }
        // ... more samples for the subject
    }
}
```

### 2. Processed Data (`<subject_name>_processed.json` or `<subject_name>_processed_LOW-HIGHHz.json`)

This file contains the signal data converted to millivolts and, optionally, filtered.

```json
{
    "subject_metadata": {
        "subject_name": "S01",
        "sampling_rate": 2000.0, // Sampling rate in Hz (KHz * 1000)
        "filter_band": [300, 3000] // [low_cutoff, high_cutoff] in Hz, or null if not filtered
    },
    "samples": {
        "S01_L_T1_d80.5_FN1.mat": {
            "signal_mv": [0.004, 0.00408, ...], // Signal in millivolts
            "filtered_signal": [0.001, 0.0015, ...], // Filtered signal in mV, or null
            "metadata": { // Original sample metadata
                "side": "L",
                "trajectory": 1,
                "depth": 80.5,
                "file_number": 1
            }
        }
        // ... more samples
    }
}
```

### 3. Spike Detection Data (`<subject_name>_spikes_detected.json`)

This file builds upon the processed data by adding detected spike information, including raw detections, refractory-filtered spikes, their waveforms, and isolation scores.

```json
{
    "subject_metadata": {
        "subject_name": "S01",
        "sampling_rate": 2000.0,
        "filter_band": [300, 3000], // or null
        "spike_detection_params": { 
            "method": "rms_multiplier",
            "n_rms_multiplier": 4.0,
            "refractory_period_before_s": 0.001,
            "refractory_period_after_s": 0.002
        },
        "spike_waveform_params": {
            "before_ms": 2.0,  // Time before spike peak for waveform extraction
            "after_ms": 3.0    // Time after spike peak for waveform extraction
        }
    },
    "samples": {
        "S01_L_T1_d80.5_FN1.mat": {
            "signal_mv": [0.004, ...],
            "filtered_signal": [0.001, ...], // or null
            "metadata": {
                "side": "L",
                "trajectory": 1,
                "depth": 80.5,
                "file_number": 1
            },
            "spikes_raw_detected": [ // List of all spikes detected by threshold crossing
                {"time_s": 0.123, "amplitude_mv": -0.085, "index": 246},
                {"time_s": 0.1245, "amplitude_mv": -0.090, "index": 249},
                {"time_s": 0.456, "amplitude_mv": -0.092, "index": 912}
            ],
            "spikes_refractory_filtered": [ // List of spikes after refractory period filtering
                {
                    "time_s": 0.123,
                    "amplitude_mv": -0.085,
                    "index": 246,
                    "waveform": [-0.02, -0.03, ..., -0.085, ..., -0.01] // Voltage values around the spike
                },
                {
                    "time_s": 0.456,
                    "amplitude_mv": -0.092,
                    "index": 912,
                    "waveform": [-0.03, -0.04, ..., -0.092, ..., -0.02]
                }
            ],
            "spike_waveform_metadata": {
                "time_axis_ms": [-2.0, -1.9, ..., 0, ..., 2.9, 3.0], // Time points for waveform plotting
                "before_ms": 2.0,
                "after_ms": 3.0
            },
            "isolation_scores": { // Quality metrics for spike detection
                "snr_ap": 2.5,      // Signal-to-Noise Ratio
                "fn_score": 0.95,    // False Negative Score
                "fp_score": 0.02,    // False Positive Score
                "isolation_score": 0.98  // Overall Isolation Score
            }
        }
        // ... more samples
    }
}
```