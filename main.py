import os
from pathlib import Path
from data_extractor import DataExtractor

def main():
    # Define the base path to your data directory
    base_path = "E:\Post-Doc\DbsData\Ephys\HadassahSurgData"  # Update this to your actual data directory path
    
    # Create output directory for processed data
    output_dir = "extracted_data"
    
    # Initialize the data extractor
    extractor = DataExtractor(base_path)
    
    # Process all subjects and save their data
    processed_files = extractor.process_all_subjects(output_dir)
    
    print("\nExtraction complete!")
    print(f"Extracted data saved in: {output_dir}")
    print("\nExtracted files:")
    for subject, file_path in processed_files.items():
        print(f"- {subject}: {file_path}")

if __name__ == "__main__":
    main() 