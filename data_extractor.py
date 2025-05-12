import os
from pathlib import Path
import scipy.io as sio
import numpy as np
from typing import Dict, List, Tuple, Optional
import json

class DataExtractor:
    def __init__(self, base_path: str):
        """
        Initialize the DataExtractor with the base path to the data.
        
        Args:
            base_path (str): Base path to the data directory
        """
        self.base_path = Path(base_path)
        self.subjects_data = {}
        
    def _convert_to_json_serializable(self, data: Dict) -> Dict:
        """
        Convert NumPy arrays in the data structure to lists for JSON serialization.
        
        Args:
            data (Dict): The data structure to convert
            
        Returns:
            Dict: JSON-serializable version of the data
        """
        if isinstance(data, np.ndarray):
            return data.tolist()
        elif isinstance(data, dict):
            return {key: self._convert_to_json_serializable(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._convert_to_json_serializable(item) for item in data]
        else:
            return data

    def process_subject_directory(self, subject_dir: str) -> Dict:
        """
        Process a single subject directory and extract relevant information.
        
        Args:
            subject_dir (str): Name of the subject directory
            
        Returns:
            Dict: Dictionary containing processed data for the subject with the following structure:
                {
                    'subject_metadata': {
                        'BitResolution': float,
                        'Gain': float,
                        'KHz': float
                    },
                    'samples': {
                        'filename.mat': {
                            'raw_signal': list,  # raw signal data
                            'side': str,         # 'lt' or 'rt'
                            'trajectory': int,   # trajectory number
                            'depth': float,      # recording depth
                            'file_number': int   # file number
                        },
                        ...
                    }
                }
        """
        subject_path = self.base_path / subject_dir
        if not subject_path.exists():
            raise FileNotFoundError(f"Subject directory {subject_dir} not found")
            
        mat_files = list(subject_path.glob("*.mat"))
        subject_data = {
            'subject_metadata': {},
            'samples': {}
        }
        
        # First pass: collect subject-level metadata
        for mat_file in mat_files:
            if self._is_valid_file(mat_file.name):
                craw_vars = self._extract_craw_data(mat_file)
                if craw_vars:
                    metadata = self._extract_metadata(craw_vars)
                    if metadata:
                        subject_data['subject_metadata'].update(metadata)
                        break  # We only need one file to get the subject metadata
        
        # Second pass: process individual samples
        for mat_file in mat_files:
            if self._is_valid_file(mat_file.name):
                sample_info = self._parse_filename(mat_file.name)
                if sample_info:
                    craw_vars = self._extract_craw_data(mat_file)
                    if craw_vars:
                        raw_signal = self._extract_raw_signal(craw_vars)
                        if raw_signal:
                            subject_data['samples'][mat_file.name] = {
                                'raw_signal': next(iter(raw_signal.values())),  # Get the raw signal
                                'side': sample_info['side'],
                                'trajectory': sample_info['trajectory'],
                                'depth': sample_info['depth'],
                                'file_number': sample_info['file_number']
                            }
        
        # Convert NumPy arrays to lists for JSON serialization
        return self._convert_to_json_serializable(subject_data)
    
    def _is_valid_file(self, filename: str) -> bool:
        """
        Check if the file matches our criteria.
        
        Args:
            filename (str): Name of the file to check
            
        Returns:
            bool: True if file is valid, False otherwise
        """
        return (
            filename.endswith('.mat') and
            '+mf' not in filename
        )
    
    def _parse_filename(self, filename: str) -> Optional[Dict]:
        """
        Parse the filename to extract relevant information.
        
        Args:
            filename (str): Name of the file to parse
            
        Returns:
            Optional[Dict]: Dictionary containing parsed information or None if invalid
        """
        try:
            # Extract side (first 2 letters)
            side = filename[:2].lower()
            if side not in ['lt', 'rt']:
                return None
                
            # Extract trajectory number (first digit after side)
            traj_num = int(filename[2])
            
            # Extract depth information
            depth_idx = filename.find('d')
            f_idx = filename.find('f')
            if depth_idx == -1:
                return None
            depth = float(filename[depth_idx + 1:f_idx])
            
            # Extract file number
            if f_idx == -1:
                return None
            file_num = int(filename[f_idx + 1:f_idx + 5])
            
            return {
                'side': side,
                'trajectory': traj_num,
                'depth': depth,
                'file_number': file_num
            }
        except (ValueError, IndexError):
            return None
    
    def _extract_craw_data(self, file_path: Path) -> Optional[Dict]:
        """
        Extract CRAW variables from a .mat file.
        
        Args:
            file_path (Path): Path to the .mat file
            
        Returns:
            Optional[Dict]: Dictionary containing raw CRAW variables from the .mat file or None if invalid.
            The variables are not processed - they are returned as loaded from the file.
        """
        try:
            # Load only the headers
            all_vars = sio.whosmat(str(file_path))  # returns list of (name, shape, dtype)

            # Filter variable names containing 'CRAW'
            craw_var_names = [name for name, *_ in all_vars if 'CRAW_02' in name]

            # Load only those variables
            craw_vars = sio.loadmat(str(file_path), variable_names=craw_var_names)
            
            if not craw_vars:
                return None

            return craw_vars
            
        except Exception as e:
            print(f"Error processing file {file_path}: {str(e)}")
            return None

    def _extract_metadata(self, craw_vars: Dict) -> Dict:
        """
        Extract metadata from CRAW variables.
        
        Args:
            craw_vars (Dict): Dictionary containing CRAW variables
            
        Returns:
            Dict: Dictionary containing extracted metadata (BitResolution, Gain, KHz)
        """
        metadata = {}
        metadata_vars = ['BitResolution', 'Gain', 'KHz']
        
        for var_name in metadata_vars:
            # Find the matching key
            matching_key = next((key for key in craw_vars if var_name in key), None)
            
            if matching_key is not None:
                value_array = craw_vars[matching_key]
                # Extract scalar value from array
                metadata[var_name] = float(value_array.item())
            else:
                metadata[var_name] = None
                
        return metadata

    def _extract_raw_signal(self, craw_vars: Dict) -> Optional[Dict]:
        """
        Extract raw signal data from CRAW variables.
        
        Args:
            craw_vars (Dict): Dictionary containing CRAW variables
            
        Returns:
            Optional[Dict]: Dictionary containing the raw CRAW_02 signal or None if invalid
        """
        try:
            # Look specifically for CRAW_02 signal
            craw_02_key = next((key for key in craw_vars if 'CRAW_02' in key), None)
            if not craw_02_key:
                return None
                
            var_data = craw_vars[craw_02_key]
            if not isinstance(var_data, np.ndarray):
                return None
                
            # Return the raw signal data
            return {craw_02_key: var_data.astype(float)}
            
        except Exception as e:
            print(f"Error extracting raw signal: {str(e)}")
            return None
    
    def process_all_subjects(self, output_dir: str = "processed_data") -> Dict:
        """
        Process all subject directories in the base path and save each subject's data in a separate file.
        
        Args:
            output_dir (str): Directory where processed data will be saved
            
        Returns:
            Dict: Dictionary containing paths to the saved files for each subject
        """
        # Create output directory if it doesn't exist
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        processed_files = {}
        for subject_dir in self.base_path.iterdir():
            if subject_dir.is_dir():
                try:
                    # Process the subject's data
                    subject_data = self.process_subject_directory(subject_dir.name)
                    
                    # Create filename for this subject's data
                    output_file = output_path / f"{subject_dir.name}_extracted.json"
                    
                    # Save to JSON file
                    with open(output_file, 'w') as f:
                        json.dump(subject_data, f, indent=4)
                    
                    processed_files[subject_dir.name] = str(output_file)
                    print(f"Processed and saved data for subject {subject_dir.name}")
                    
                except Exception as e:
                    print(f"Error processing subject {subject_dir.name}: {str(e)}")
                    
        return processed_files
