%in MAIN 041114
% test_sorting
%IN:   rawAnalog - raw analog data 
%         apIndex - the index in raw data of the spikes of all units.
%                            the index may have a shift from the beginning  of the spike 
%                             but the shift MUST be the same for all spikes in that unit
%                             (shifts may differ between units). The function excepts two formats:
%                               1. a pXn matrix where p is the number of units and n is the maximum number
%                                   of spikes per unit. Each row contains the indices for all spikes. The
%                                   cells following the last index will contain NaN, unless the row
%                                   contains a unit containing n spikes.
%                               2. a cell array in which each cell i contains a vector of indices specifying
%                                   spike times for the unit i.
%          UnitNum - the number of the unit to analyze. UnitNum is the index of a row if
%                                apIndex is a matrix or the index of a cell if apIndex is a cell array.

% OUT: snrAp - the signal to noise ratio - the signal is p2p value
%                                the noise is the sd of the analogAp  after subtracting the average 
%          snrBeforeAp - the signal to noise ratio-  the signal is p2p value
%                                the noise is the sd of the analog signal BEFORE the spike
%          fnScore -  Estimation of the number of spikes missed in apIndex
%          fpScore -  Estimation of the number of spike that are actually noise events
%          isolationScore1  -  scores the difference between the spike events and noise
%                                                       events, noise being defined as all non-unit threshold crossing events
%          analogAp - matrix(N,P)  of a sample from spikes waveform aligned to the minimal peak 
%          analog - high pass filtered analog            
%          noiseInx - index in analog signal of high noise events
%          highNoise - the highNoise events
%          apIndex - the index of the spikes after shifting them to minimal peak 
%           distinctionScore - scores the difference between UnitNum to all other units
%           isolation score2 - scores the difference between each unit to all other threshold
%                                                       crossing events (noise + other units) - compare with isolationScore1.
function [snrAp, snrBeforeAp, fnScore, fpScore, isolationScore1, analogAp, ...
        analog, noiseInx, highNoise, apIndex, distinctionScore, isolationScore2]   ...
    = test_sorting_IsoDist(rawAnalog, apIndex,UnitNum) 
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
global  MINTIME;                                  % minimum number of minutes each file has to be in order to apply for analysis
 global MINSPIKES;                             % minimum number of spikes each unit has to contain in order to apply for analysis

%global TEST_SORT_ANALOG_KHZ;  % sampeling rate of the analog signal
% globals for function  plot_featurs 
global PLOT_FEATURE_HANDLER;   
global PLOT_FEATURE_CURR_ROW;
global PLOT_FEATURE_MAX_ROWS;
global RUNS;                                            % number of runs over the isolation score calculation (runs are averaged)
% global TEST_SORT_DIGITAL_KHZ;

TEST_SORT_BIN_SIZE = 50; 
TEST_SORT_SPLIT_RATE = 2; 
TEST_SORT_MAX_EVENTS = 3000;
TEST_SORT_KNN =31; % must be odd
TEST_SORT_CARC_CONST = 0.1;
TEST_SORT_SPIKE_THRESHOLD_RATIO = 2;
%TEST_SORT_SPIKE_THRESHOLD = 2.5;
TEST_SORT_SPIKE_THRESHOLD_MIN_FRACTION = 0.05;
TEST_SORT_SD_FACTOR =5;
TEST_SORT_PLOT =0;
PLOT_FEATURE_MAX_ROWS = 4;
TEST_SORT_ANALOG_KHZ = 44;
MINTIME=0;%2;
MINSPIKES=0;%200;
RUNS=2;
% TEST_SORT_DIGITAL_KHZ=40;

try
    error(nargchk(3,3,nargin))
    if(isempty(apIndex))
         warning('no spikes detected in the analog signal can not test the sorting');
         snrAp = NaN;  snrBeforeAp =NaN;  fnScore =NaN; fpScore =NaN; isolationScore1 =NaN; isolationScore2 =NaN;distinctionScore =NaN;
         analogAp = []; analog = [];  noiseInx =[];  highNoise =[];  apIndex =[];
         return;
    end

    % if UnitSpikeIndex is a cell array, it will be converted into a matrix with NaN
    % replacing the missing values

    if iscell(apIndex)
        temp=apIndex;
        clear apIndex;
        apIndex=NaN(numel(temp),max(cellfun(@numel,temp)));
        for i=1:numel(temp)
            apIndex(i,1:numel(temp{i}))=temp{i};
        end;
        clear temp;
    end;
    apIndex=apIndex(apIndex<length(rawAnalog)); 
    [analog, analogAp , highNoise ,  apIndex, noiseInx] = get_analog_events2(rawAnalog, apIndex,UnitNum); 

    allUnitSpikes_temp=reshape(apIndex',numel(apIndex),1);
    allUnitSpikes_temp(isnan(allUnitSpikes_temp(:,1)),:)=[];
    allUnitSpikes=allUnitSpikes_temp';  % This is a vector of all the spikes from all units

%     [p2pSnr, ~]  = snr_test(analog, analogAp,allUnitSpikes);  %note that the SNR process utilizes the average spikeform for the chosen unit only, but compares it to noise that is defined as a time interval with no spikes of ANY kind
     [ fnScore fpScore, isolationScore1 ]  = knn_test(analogAp, highNoise); 
     if size(apIndex,1)==1
         isolationScore2=isolationScore1;
     else

         [~, analogAp2 , highNoise2 ,  ~, ~ ] = get_analog_events(rawAnalog, apIndex(UnitNum,1:find(~isnan(apIndex(UnitNum,:)),1,'last'))); 
    size(highNoise2);
         [ ~, ~, isolationScore2 ]  = knn_test(analogAp2, highNoise2); 
     end;

    %     snrAp = p2pSnr(2);
    %     snrBeforeAp = p2pSnr(3);
    snrAp = NaN;  snrBeforeAp =NaN;  
    % the following lines create an array that suits - in size and format -
    % with the input parameter of the function distinction_score.

    analogApCellArray{1}=analogAp;
    numSpikes(1)=length(find(~isnan(apIndex(UnitNum,:))));
    ratio=size(analogAp,1)/numSpikes(1);
    a=size(apIndex,1);
    index=2;
    for i=1:a
        if i~=UnitNum
            [~,analogApCellArray{index},~,~,~]=get_analog_events2(rawAnalog, apIndex,i);
            numSpikes(index)=length(find(~isnan(apIndex(i,:))));
            tempratio=size(analogApCellArray{index},1)/numSpikes(index);
            if tempratio<ratio
                ratio=tempratio;
            end;
            index=index+1;
        end;
    end;

    for i=1:index-1
        analogApCellArray{i}=analogApCellArray{i}(1:floor(ratio*numSpikes(i)),:);
    end;
    if a>1
        [ distinctionScore ]  = distinction_test(analogApCellArray);
    else
        distinctionScore=nan;
    end;
catch
         snrAp = NaN;  snrBeforeAp =NaN;  fnScore =NaN; fpScore =NaN; isolationScore1 =NaN; isolationScore2 =NaN;distinctionScore =NaN;
         analogAp = []; analog = [];  noiseInx =[];  highNoise =[];  apIndex =[];
         return;
end;
