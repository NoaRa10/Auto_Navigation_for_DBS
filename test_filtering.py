from test_filter_helper_func import test_filtering

def main():
    # Set parameters
    input_file = "processed_data/Subject_1_processed_300-3000Hz.json"  # Change this to test different files
    output_file = "filter_test.png"
    
    try:
        test_filtering(input_file, output_file)
        print("\nTest completed successfully!")
    except Exception as e:
        print(f"\nError during testing: {str(e)}")

if __name__ == "__main__":
    main() 