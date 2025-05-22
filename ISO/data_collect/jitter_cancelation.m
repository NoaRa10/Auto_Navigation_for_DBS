% jitter cancelation - upsample the data by interpolating the data
%IN: rawData - data before interpolation 
%OUT: smoothData - data after interpolation
function [ smoothData ]   =  jitter_cancelation(rawData)
global TEST_SORT_SPLIT_RATE;
signalLength = size(rawData,2);
 smoothLength = signalLength*TEST_SORT_SPLIT_RATE;
  % A column vector of time samples;
 t =  (1:signalLength)';  
 % times at which to interpolate data
 ts = linspace(1, signalLength, smoothLength)';   
 convData = spline(t', rawData, ts')' ;
 smoothData = convData';
