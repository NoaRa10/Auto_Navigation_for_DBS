# DBS Data Processor

This project processes DBS (Deep Brain Stimulation) electrophysiological data from .mat files, extracting and processing CRAW data according to specific criteria.

## Requirements

- Python 3.7 or higher
- Required packages are listed in `requirements.txt`

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

## Data Processing Details

The script processes files according to the following criteria:
- Only .mat files are processed
- Files must not contain "MF" in their name
- Files must contain "F" followed by 4 digits
- CRAW data is extracted and processed using bit resolution and gain values

## Output

The processed data is saved in JSON format with the following structure:
```json
{
    "subject_name": {
        "file_info": [
            {
                "side": "le/ri",
                "trajectory": number,
                "depth": number,
                "file_number": number
            }
        ],
        "craw_data": {
            "filename": {
                "CRAW_variable_name": processed_data_array
            }
        }
    }
}
```