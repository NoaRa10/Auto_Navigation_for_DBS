% get the 'analog' spikes 
% IN: analog - vector of the analog signal  
%         apIndex - the index of the action potentials 
%         numEvent - number of events
%         mayHaveShift - 0: no shift between analog and apIndex
%                                         else: the data may have a shift                                       
% OUT: res - matrix(N,P), The rows of the matrix are aligned signals of the spike
%          shift - the shift of the apIndex compared to min value of the  signal 

function [res, shift] = get_analog_ap(analog, apIndex, numEvents, mayHaveShift)
global TEST_SORT_BIN_SIZE;
error(nargchk(4,4,nargin));
if(numEvents > size(apIndex,2))
    error('numEvents is larger than the actual numer of events');
end
binSize = TEST_SORT_BIN_SIZE;
maxLength = 40*binSize;


apIndex = apIndex(randperm(length(apIndex)));

apIndex = apIndex(1:numEvents);

inxVec = -maxLength:maxLength;

% remove events that are too short ( end of analog and begining of analog)
apIndex = apIndex(find(  (apIndex > maxLength) & (apIndex < size(analog,2) -maxLength +1)));
if(isempty(apIndex))
    res = [];
    shift =[];
    warning('None of the  digital events match the analog signal ');
    return;
end

matInx = apIndex(ones(size(inxVec)),:)';
matInx = matInx + inxVec(ones(size(apIndex)) , :);
res = analog(matInx); 
if(mayHaveShift)
    [minVal, minInx]  = min(mean(res,1)); 
    shift = ceil(size(res,2)/2) -  minInx; 
    %disp(['shift = ' num2str(shift)]);
    if( (minInx + binSize) > 2*maxLength   |  minInx - binSize <  1)
       error(' the shift of the data is to long');
    end
else
    minInx = maxLength;
end
res = res(:, (minInx - binSize) : (minInx+binSize));

res = jitter_cancelation(res);
res = align_data(res);

% set all  events mean to 0  
meanVal = mean(res')';
res = res - meanVal(:, ones(1,size(res, 2)));
