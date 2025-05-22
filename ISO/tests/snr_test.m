% perform a signal to noise tests
% IN: analog - analog signal
%        analogAp(N,P) - matrix of the analog signal of the spike
% OUT: res there are meny ways to calculate ratio between  noise and the signal 
%          ROW indices  are the signal estimations 
%          1 - peak to peak estimation
%          2 - signal energy
%          COLOUM indices are the noise estimations
%         1 - allNoiseStd  - std of all the analog signal
%         2 - apSignalNoise - the std of the difference between the meanSignal and the  signal
%         3 -  beforeApNoise - calc the std of the signal before the spike   

function [ p2pSnr, energySnr]  = snr_test(analog, analogAp, apIndex)
global TEST_SORT_BIN_SIZE;
global TEST_SORT_SD_FACTOR;
error(nargchk(3,3,nargin))
if(size(analogAp,1)<2)
    warning('can not calculate SNR with less than 2 spikes');
    p2pSnr = [NaN NaN NaN];
    energySnr = [NaN NaN NaN];
    return;
end
    
binSize = TEST_SORT_BIN_SIZE;
sdFactor = TEST_SORT_SD_FACTOR;
meanSignal = mean(analogAp);
signalSize = size(meanSignal,2);

allNoiseVal = sdFactor *std(analog);
noiseAp = analogAp - repmat(meanSignal, size(analogAp, 1) ,1);
apNoiseVal = sdFactor*std(reshape(noiseAp, 1, size(noiseAp,1)* size(noiseAp,2)));

% calc the std before the spike  - use only traces with no spikes 
% shift right
circShift = circshift(apIndex, [0 1]);
% get the time difference between spikes
diff = apIndex- circShift;
% use spikes that are far from other spikes.
spikeInx = apIndex(find(diff > 3 *binSize));

inxVec  =1:binSize;
inx = spikeInx - 2* binSize;
inx = inx(find(inx >0 & inx+binSize < size(analog,2)));
matInx = inx(ones(size(inxVec)),:)';
matInx = matInx + inxVec(ones(size(inx)) , :);
vals = analog(matInx); 
beforeApNoise = sdFactor*std(reshape(vals, 1, size(vals,1)* size(vals,2)));

noiseEstimation = [ allNoiseVal apNoiseVal beforeApNoise];

signalPeak2Peak =   max(meanSignal) - min(meanSignal);
signalEnergy =   sqrt( mean(meanSignal.^2));
 
signalEstimation = [signalPeak2Peak , signalEnergy] ;

p2pSnr =  signalEstimation(1)./ noiseEstimation;
energySnr = 20*log10(signalEstimation(2)./ noiseEstimation);

