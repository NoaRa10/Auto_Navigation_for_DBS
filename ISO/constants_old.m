% constants of the program 

clear global TEST_SORT_BIN_SIZE  TEST_SORT_SPLIT_RATE TEST_SORT_MAX_EVENTS TEST_SORT_KNN;
clear global TEST_SORT_CARC_CONST  TEST_SORT_SPIKE_THRESHOLD_RATIO  TEST_SORT_SPIKE_THRESHOLD PLOT_FEATURE_HANDLER;
clear global PLOT_FEATURE_CURR_ROW PLOT_FEATURE_MAX_ROWS TEST_SORT_PLOT ; 
clear global TEST_SORT_ANALOG_KHZ TEST_SORT_SPIKE_THRESHOLD_MIN_FRACTION;
global TEST_SORT_BIN_SIZE;      % size of each event  
global TEST_SORT_SPLIT_RATE; %interpolation  split 
global TEST_SORT_MAX_EVENTS; % max number of events for tests
global TEST_SORT_KNN;                 % the K used in K  nearest nieghbor    
global TEST_SORT_CARC_CONST; % constant for calculating the isolation score
global TEST_SORT_SPIKE_THRESHOLD; % the threshold used for noise detection
global TEST_SORT_SPIKE_THRESHOLD_RATIO; % the ratio between spike peak and threshold - used for noise detection
global TEST_SORT_SPIKE_THRESHOLD_MIN_FRACTION; % the precentage of spikes used for calculation the threshold
global TEST_SORT_SD_FACTOR;   % factor used for calculating the snr
global TEST_SORT_PLOT;                % 1 plot results 0 do not plot results 
global TEST_SORT_ANALOG_KHZ; % the analog sampling rate
%global TEST_SORT_ANALOG_KHZ;  % sampeling rate of the analog signal
% globals for function  plot_featurs 
global PLOT_FEATURE_HANDLER;   
global PLOT_FEATURE_CURR_ROW;
global PLOT_FEATURE_MAX_ROWS;

 
TEST_SORT_BIN_SIZE = 36; 
TEST_SORT_SPLIT_RATE = 4; 
TEST_SORT_MAX_EVENTS = 15000; 
TEST_SORT_KNN =31; % must be odd
TEST_SORT_CARC_CONST = 0.1;
TEST_SORT_SPIKE_THRESHOLD_RATIO = 2;
%TEST_SORT_SPIKE_THRESHOLD = 2.5;
TEST_SORT_SPIKE_THRESHOLD_MIN_FRACTION = 0.05;
TEST_SORT_SD_FACTOR =5;
TEST_SORT_PLOT =0;
PLOT_FEATURE_MAX_ROWS = 4;
TEST_SORT_ANALOG_KHZ = 25;