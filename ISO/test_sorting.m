% test_sorting
%IN:   rawAnalog - raw analog data 
%         apIndex - the index in raw data of the spikes 
%                            the index may have a shift from the beginning  of the spike 
%                             but the shift MUST be the same for all spikes
% OUT: snrAp - the signal to noise ratio - the signal is p2p value
%                                the noise is the sd of the analogAp  after subtracting the average 
%          snrBeforeAp - the signal to noise ratio-  the signal is p2p value
%                                the noise is the sd of the analog signal BEFORE the spike
%          fnScore -  Estimation of the number of spikes missed in apIndex
%          fpScore -  Estimation of the number of spike that are actually noise events
%          isolationScore  -  scores the difference between the spike events and noise events  
%          analogAp - matrix(N,P)  of a sample from spikes waveform aligned to the minimal peak 
%          analog - high pass filtered analog            
%          noiseInx - index in analog signal of high noise events
%          highNoise - the highNoise events
%          apIndex - the index of the spikes after shifting them to minimal peak 
function [snrAp, snrBeforeAp, fnScore, fpScore, isolationScore,  analogAp, ...
        analog, noiseInx, highNoise, apIndex ]   ...
    = test_sorting(rawAnalog, apIndex) 
error(nargchk(2,2,nargin))
if(length(apIndex) ==0)
     warning('no spikes detected in the analog signal can not test the sorting');
     snrAp = NaN;  snrBeforeAp =NaN;  fnScore =NaN; fpScore =NaN; isolationScore =NaN; 
     analogAp = []; analog = [];  noiseInx =[];  highNoise =[];  apIndex =[];
     return;
end

[analog, analogAp , highNoise ,  apIndex, noiseInx ] = get_analog_events(rawAnalog, apIndex); 
[p2pSnr, energySnr]  = snr_test(analog, analogAp,apIndex);
snrAp = p2pSnr(2);
snrBeforeAp = p2pSnr(3);
 [ fnScore fpScore, isolationScore ]  = knn_test(analogAp, highNoise); 