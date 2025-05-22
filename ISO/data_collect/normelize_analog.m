% normelize analog data
% IN:  analog  - raw analog signal 
% OUT: res - high pass filtered analog   
                     
function [highPass ] = normelize_analog(analog)
global TEST_SORT_ANALOG_KHZ;
nyquist = TEST_SORT_ANALOG_KHZ*1000/2;
Wp = [300/nyquist 8000/nyquist];
Ws = [100/nyquist 10000/nyquist];
[n Wn] = buttord(Wp,Ws, 3, 10);
[b a] =  butter(n,Wn);
highPass = filtfilt(b,a,analog);

