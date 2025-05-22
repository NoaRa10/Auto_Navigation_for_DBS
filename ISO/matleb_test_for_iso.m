% Specify the path to your JSON file
raw_sig_filename = 'C:\Users\noara\Auto_Navigation_for_DBS\processed_data\Subject_2_processed_300-3000Hz.json';

% Read the entire file as a character vector
jsonText = fileread(raw_sig_filename);

% Decode the JSON text into a MATLAB structure
raw_data = jsondecode(jsonText);

% Specify the path to your JSON file
spk_sig_filename = 'C:\Users\noara\Auto_Navigation_for_DBS\spikes_data\Subject_2_spikes_detected.json';

% Read the entire file as a character vector
jsonText = fileread(spk_sig_filename);

% Decode the JSON text into a MATLAB structure
spk_data = jsondecode(jsonText);

rawAnalog = raw_data.samples.lt1d0_170f0001_mat.filtered_signal;
apIndex_struct = spk_data.samples.lt1d0_170f0001_mat.spikes_refractory_filtered;
apIndex = [apIndex_struct.index]+1;

fs = raw_data.subject_metadata.sampling_rate;
time_vec = (0:length(rawAnalog)-1) / fs;
plot(time_vec, rawAnalog)
hold on
plot(time_vec(apIndex), rawAnalog(apIndex), 'r*'); 

[snrAp, ~, fnScore, fpScore, isolationScore1] = test_sorting_IsoDist(rawAnalog, apIndex, 1);