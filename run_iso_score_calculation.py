from isolation_score_helper_func import calculate_isolation_scores

def main():
    PROCESSED_DIR = "processed_data"
    SPIKES_DATA_DIR = "spikes_data"
    calculate_isolation_scores(PROCESSED_DIR, SPIKES_DATA_DIR)

if __name__ == "__main__":
    main() 