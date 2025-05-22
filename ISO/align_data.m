% align data - align data by the minimum value 
%IN:  data(N,P) - unaligned data   P = (2*(binSize) +1)*splitRate;  
%OUT: res(N,P) - aligned data        P =  binSize*splitRate;
function [res] = align_data(data)
global TEST_SORT_SPLIT_RATE;
global TEST_SORT_BIN_SIZE;

binSize = TEST_SORT_BIN_SIZE;
splitRate = TEST_SORT_SPLIT_RATE;

if(size(data,2) ~=   (2*binSize  +1)* splitRate)
    error('data length %d is incorrect',  size(data,2));
end

% align data by min value
apSize =  binSize * splitRate;
dataLength = size(data,2);
numEvents = size(data,1);

mid = ceil(size(data,2) / 2);
maxShift =  splitRate * 4; 
% align by min value
[minVal minIndex] =  min(data(: , (mid-maxShift):(mid+maxShift))' );
minIndex = minIndex + mid - maxShift;
firstInx = (minIndex - round(apSize/3));
lastInx =  (minIndex + round(apSize*2/3));
dataT = data';
colInx = 1:numEvents;  
firstInx = firstInx +  (colInx-1) *(dataLength);   
matInx = [];
for i =0:apSize-1; 
    matInx = cat(1, matInx, firstInx + i) ; 
end
res = dataT(matInx');
% for some reason when there is only one row in data res is a column vector 
if(size(data,1) ==1)
    res = res';
end
