function [shift] = get_analog_digital_delay(analog, apIndex, sampeling_rate)

MAX_DELAY = 10;
max_delay = round(MAX_DELAY * sampeling_rate);

apIndex   =  apIndex(find(apIndex - max_delay > 0  & apIndex  + max_delay < length(analog)));
if(isempty(apIndex))
    error('could not calculate delay');
end
apSize = min(length(apIndex), 200);
apIndex= apIndex(1:apSize);
long_spike = zeros(1,max_delay*2+1);
for j=1:length(apIndex)
    long_spike =  long_spike + analog((apIndex(j) -max_delay):(apIndex(j)+max_delay));
end
long_spike = long_spike / length(apIndex);
% deal with the delay
[val, peak_inx]  =min(long_spike);
shift = max_delay -peak_inx ;
