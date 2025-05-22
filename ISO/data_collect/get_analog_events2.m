% get_analog_events
% split the analog to 3 sets 
% in: rawAnalog    - raw analog signal 
%         apIndex - the index in raw data of the spikes of all units.
%                            the index may have a shift from the beginning  of the spike 
%                             but the shift MUST be the same for all spikes in that unit
%                             (shifts may differ between units). apIndex is a pXn matrix where
%                             p is the number of units and n is the maximum number of spikes
%                             per unit. Each row contains the indices for all spikes. The
%                             cells following the last index will contain NaN, unless the row
%                             contains a unit containing n spikes.
%          UnitNum - the number of the unit to analyze, the index of a row in apIndex.

% out:  ALL output parameters are analog signals after up-sampeling the data
%           analog- the normelized analog
%          apAnalog  - Each rows of the matrix is the analog signal of a spikes     
%                                      the data is aligned to the minimal peak    
%           highNoise  - Each row of the matrix is the analog signal of a high noise event that is not a spike (of any spikeform)                                     
%           apInx - the index of the spikes after fixing the shift
%           noiseInx -the index of the high noise events
function [ analog, apAnalog, highNoise,  apInx, noiseInx] =  get_analog_events2(rawAnalog, apIndex,UnitNum)
global TEST_SORT_MAX_EVENTS;
global TEST_SORT_SPIKE_THRESHOLD_RATIO;
% global TEST_SORT_SPIKE_THRESHOLD;
global TEST_SORT_SPIKE_THRESHOLD_MIN_FRACTION;
min_frac = TEST_SORT_SPIKE_THRESHOLD_MIN_FRACTION;
error(nargchk(3,3,nargin))
SignalUnits=apIndex(UnitNum,~isnan(apIndex(UnitNum,:)));
numAp = min([TEST_SORT_MAX_EVENTS, length(SignalUnits)]);
analog  = normelize_analog(double(rawAnalog));
% analog=rawAnalog;
% figure;
% plot(1:500200,analog(1:500200),1:500200,rawAnalog(1:500200))

[apAnalog  shift]  = get_analog_ap(analog, SignalUnits, numAp,1);
apInx= apIndex - shift;
[~, min_inx] =  min(mean(apAnalog,1)); 

% threshold =min_val /TEST_SORT_SPIKE_THRESHOLD_RATIO;
% threshold = max( threshold , -std(analog) *TEST_SORT_SPIKE_THRESHOLD);
% [highNoise, noiseInx] =  get_high_noise_events(analog, apInx, threshold);

% is the noise cluster is too small make it bigger by using a threshold
% relative to the small spike events
% if(length(noiseInx) < length(apIndex))
    [sort_val sort_inx] = sort(apAnalog(:, min_inx));
    use_for_threshold = ceil(length(sort_val)* min_frac);
    lower_avg = mean(sort_val(end+1-use_for_threshold:end));
    threshold =lower_avg /TEST_SORT_SPIKE_THRESHOLD_RATIO;
    %threshold = max( threshold , -std(analog) *TEST_SORT_SPIKE_THRESHOLD);
    
     [highNoise, noiseInx] =  get_high_noise_events2(analog, apInx, threshold);
     
%end

% save the porportion between the number of noise and spike events
total_spikes = length(SignalUnits); % total amounts of spikes in all the data
total_noise = length(noiseInx); % total amount of noise events
num_analog_spikes = size(apAnalog,1); % number of analog segments taken for spikes
num_analog_noise = size(highNoise,1);% number of analog segments taken for noise

if(total_spikes > total_noise)
     num_test_spikes= num_analog_spikes;
     num_test_noise = floor(total_noise * num_analog_spikes /total_spikes);
else
    num_test_noise = num_analog_noise;
    num_test_spikes = floor(total_spikes * num_analog_noise / total_noise);
end

% the following condition  was added to insure that there will be enough spikes to do the
% analysis. In previous versions, if for example the were 2000 spikes but 2,000,000 noise events -
% the algorithm would have taken only about 20 of the spikes to assure that the sampling from
% the spike and noise would be in the same ratios (the isolation score is not normalized and
% the more noise events you put in - the smaller the score is). Now, there is a minimum of 100 spikes.

% if num_test_spikes<100 && total_spikes>=100 
%     num_test_spikes=100;
%     TEST_SORT_MAX_EVENTS=floor(total_noise * num_test_spikes /total_spikes);
%      [highNoise, noiseInx] =  get_high_noise_events2(analog, apInx, threshold);
%     num_test_noise = floor(total_noise * num_test_spikes /total_spikes);
% end;

apAnalog = apAnalog(1:min(num_test_spikes, size(apAnalog,1)),:);
highNoise= highNoise(1:min(num_test_noise, size(highNoise,1)),:);