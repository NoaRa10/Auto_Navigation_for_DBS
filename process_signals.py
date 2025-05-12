from pathlib import Path
from signal_processor import SignalProcessor
import json

def verify_and_create_directories(directories: dict) -> None:
    """
    Verify if directories exist and create them if they don't.
    
    Args:
        directories (dict): Dictionary of directory names and their paths
    """
    for dir_name, dir_path in directories.items():
        path = Path(dir_path)
        if not path.exists():
            print(f"Creating {dir_name} directory: {dir_path}")
            path.mkdir(parents=True, exist_ok=True)
        else:
            print(f"{dir_name} directory exists: {dir_path}")

def main():
    # Set your parameters here
    input_dir = 'extracted_data'  # Directory containing input .mat files
    output_dir = 'processed_data'  # Directory to save processed data
    
    # Filter parameters (set to None if no filtering needed)
    low_freq = 300  # Low cutoff frequency in Hz
    high_freq = 3000  # High cutoff frequency in Hz
    
    # Subject parameter (set to None to process all subjects)
    subject = 'Subject_1'  # Set to subject name (e.g., 'subject1') to process specific subject
    
    # Verify and create directories
    directories = {
        'Input': input_dir,
        'Output': output_dir
    }
    verify_and_create_directories(directories)
    
    # Validate filter frequencies
    filter_band = None
    if low_freq is not None and high_freq is not None:
        if low_freq >= high_freq:
            raise ValueError("low_freq must be less than high_freq")
        filter_band = (low_freq, high_freq)
    
    # Initialize processor
    processor = SignalProcessor(input_dir)
    
    # Process data
    if subject:
        # Process single subject
        input_file = Path(input_dir) / f"{subject}_extracted.json"
        output_file = Path(output_dir) / f"{subject}_processed.json"
        if filter_band:
            output_file = Path(output_dir) / f"{subject}_processed_{int(filter_band[0])}-{int(filter_band[1])}Hz.json"
            
        print(f"\nProcessing subject: {subject}")
        print(f"Input file: {input_file}")
        print(f"Output file: {output_file}")
        
        # Process and save data
        processed_data = processor.process_subject(subject, filter_band)
        print("Data processed successfully")
        
        # Save processed data
        with open(output_file, 'w') as f:
            json.dump(processed_data, f, indent=4)
        print(f"Data saved to: {output_file}")
    else:
        # Process all subjects
        print("\nProcessing all subjects...")
        processor.process_all_subjects(output_dir, filter_band)
    
    print(f"\nProcessing complete!")
    print(f"Output directory: {output_dir}")
    if filter_band:
        print(f"Applied bandpass filter: {filter_band[0]}-{filter_band[1]} Hz")

if __name__ == "__main__":
    main() 