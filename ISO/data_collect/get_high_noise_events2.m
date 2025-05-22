% get_high_noise_events2 
% use peak to peak difference to define high noise events 
% IN:   analog - the analog signal 
%          apIndex - index of the ap in analog (these events are not noise)
%          threshold - the threshold for detection of noise events
% OUT: res - a matrix of the noise events after up sampeling  and alignment to min 
%          noiseInx - index of the noise event in analog
function [ res,  noiseInx] =  get_high_noise_events2(analog, apIndex,threshold)
error(nargchk(3,3,nargin))
global TEST_SORT_MAX_EVENTS;
inx = find(analog < threshold  );

% Each high noise event is more than one index 
% use only one index for each event 
diffInx = inx-circshift(inx,[0, 1])  ;
first = [1, find(diffInx > 4 )];  %  isolate events 
last = first -1;
last = [last(2:end), size(inx,2)]; 

eventInx= zeros(1,size(first,2)); 
for i=1:size(first,2)
    [val I] = min(analog(inx(first(i)):inx(last(i)) ));
   eventInx(i) = inx(first(i)) + I-1;
end
% move action potentials from noise
% commonVals =[];
% for k=1:size(apIndex,1)
%     for j=1:size(apIndex,2)
%         for i = -2:2
%             commonVals = [commonVals intersect(eventInx, apIndex(k,j)+ i)];
%         end;
%     end;
% end;
% noiseInx2 = setdiff(eventInx,commonVals );
noiseInx = setdiff(eventInx,[apIndex(:)-2,apIndex(:)-1,apIndex(:),apIndex(:)+1,apIndex(:)+2]);
numNoise =  min([TEST_SORT_MAX_EVENTS, length(noiseInx)]); 
if(size(noiseInx, 2) == 0)
    res = [];
    return;
end

res = get_analog_ap(analog, noiseInx, numNoise,0);
