import json
from pathlib import Path
from typing import Dict, Optional

from isolation_score_calculator import IsolationScoreCalculator

def load_json_data(file_path: Path) -> Dict:
    """Load JSON data from file"""
    with open(file_path, 'r') as f:
        return json.load(f)

def save_json_data(file_path: Path, data: Dict) -> None:
    """Save JSON data to file"""
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

def process_single_sample(calculator: IsolationScoreCalculator, 
                         processed_data: Dict, 
                         spikes_data: Dict,
                         sample_key: str) -> Optional[Dict[str, float]]:
    """
    Process a single sample and calculate its isolation scores.
    
    Returns None if the sample cannot be processed.
    """
    # Get raw analog data
    raw_analog = processed_data['samples'][sample_key].get('filtered_signal')
    if not raw_analog:
        print(f"No filtered_signal found for sample {sample_key}, skipping...")
        return None

    # Get spike indices
    spikes = spikes_data['samples'][sample_key].get('spikes_refractory_filtered', [])
    if not spikes:
        print(f"No spikes found for sample {sample_key}, skipping...")
        return None

    spike_indices = [spike['index'] for spike in spikes if 'index' in spike]
    if not spike_indices:
        print(f"No spike indices found for sample {sample_key}, skipping...")
        return None

    print(f"Calculating isolation scores for sample {sample_key}...")
    return calculator.calculate_isolation_scores(raw_analog, spike_indices)

def calculate_isolation_scores(processed_dir: str, spikes_data_dir: str) -> None:
    """
    Calculate isolation scores for all subjects and samples, updating the spike detection files.
    
    Parameters:
    -----------
    processed_dir : str
        Path to the directory containing processed data JSONs
    spikes_data_dir : str
        Path to the directory containing spike detection JSONs
    """
    processed_dir = Path(processed_dir)
    spikes_data_dir = Path(spikes_data_dir)

    # Get all subject numbers
    subject_numbers = {
        file_path.name.split("_")[1]
        for file_path in spikes_data_dir.glob("Subject_*_spikes_detected.json")
    }
    print(f"Found subjects: {sorted(subject_numbers)}")

    with IsolationScoreCalculator() as calculator:
        for subject_num in sorted(subject_numbers):
            print(f"\nProcessing Subject_{subject_num}...")
            
            # Get file paths
            spikes_file = spikes_data_dir / f"Subject_{subject_num}_spikes_detected.json"
            processed_file = processed_dir / f"Subject_{subject_num}_processed_300-3000Hz.json"
            
            if not all(f.exists() for f in [spikes_file, processed_file]):
                print(f"Missing files for Subject_{subject_num}, skipping...")
                continue

            try:
                # Load data
                spikes_data = load_json_data(spikes_file)
                processed_data = load_json_data(processed_file)

                # Process each sample
                for sample_key in processed_data.get('samples', {}).keys():
                    if sample_key not in spikes_data.get('samples', {}):
                        continue

                    scores = process_single_sample(calculator, processed_data, spikes_data, sample_key)
                    if scores:
                        # Update the spikes data with the new scores
                        spikes_data['samples'][sample_key]['isolation_scores'] = scores

                # Save updated spikes data
                save_json_data(spikes_file, spikes_data)
                print(f"Updated isolation scores saved to {spikes_file}")

            except Exception as e:
                print(f"Error processing Subject_{subject_num}: {str(e)}")
                continue 