function [distinction] = distinction_test (analogAp) 

% This function returns the distinction score for the unit whose action potential are 
% archived (in analog form) in the first cell in the cell array analogAp. a distinction 
% score is a measure of the difference between a specific unit and all other units 
% in the file.

% This distinction calculation is similar to that of the isolation score. Both check
% the "distances" in an n-dimension space (n being the number of datapoints in the 
% analog spikeform) between different spikes in the array and compare this to
% "distances" from noise events. However, while the "isolation score" defines "noise"
% as any threshold crossing event and checks whether a certain unit is
% distinguishable from background biological and non-biological noise, the
% "distinction score" only takes other spike forms as noise, thus checking whether
% the unit is distinguishable from other spikes. Simply put, the more different two
% units' spikes are, the larger the distinction score for the units, and vice versa.

% Notes regarding the calculation and the rational behind it can be found in the
% "knn_unit" function and the accompaning manuscript for the isolation score :
%                   Joshua M, Elias S, Levine O, Bergman H (2007) Quantifying the isolation
%                   quality of extracellularly recorded action potentials. J Neurosci
%                   Methods 163:267–282.

% IN - analogAp is a cell array in which each cell contains spikeforms associated
%          with a single unit. The first cell is the one for which the isolation score is
%          calculated.
% OUT - distinction is the distinction score which is normalized between 0 and 1.

global TEST_SORT_CARC_CONST;

error(nargchk(1,1,nargin));

numUnits=numel(analogAp);

if numUnits<2
     warning('There musy be at least two units to check unit distinction');
     distinction =NaN;
     return;
end

numCells=zeros(numUnits,1);
for i=1:numUnits
    if(size(analogAp{i},1) <2)
        distinction =0;
        return;        
    end;
        numSpikes(i)=size(analogAp{i},1);
end;

carcConst = TEST_SORT_CARC_CONST;

% these are random groups becouse randomization of the order  was performed in get_analog_ap
allTrain=[];
for i=1:numUnits
    allTrain = [allTrain ; analogAp{i}(:,:)];
end;

trApSize = size(analogAp{1},1);
trNoiseSize = size(allTrain,1)-trApSize;

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% find the distance between   all events  - use (a-b)^2 = a'a - 2ab' + b'b 
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
trainSqr = sum( (allTrain .* allTrain)');
trainSqrTr = trainSqr';

mulMat   =  allTrain * allTrain';

onesVec = ones(1,trApSize+trNoiseSize);
% calc the distance between noise events to Ap events
distMat = trainSqrTr(:, onesVec)  -2* mulMat + trainSqr(onesVec,:);
% because of precision problems the diagonal  might not be 0;
for j=1:size(distMat,1)
    distMat(j,j) =0;
end
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
% ISOLATION -  isolation of the signal cluster from the  noise cluster 
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

distSS = sqrt(distMat(1:trApSize, 1:trApSize)); 
%  distNN = sqrt(distMat( trApSize+1:end,trApSize+1:end));  
 distSN = sqrt(distMat(1:trApSize, trApSize+1:end));

 % carectaristic distance - the average distance between 2 signals multiplied by carcConst
 carcDist = mean(mean(distSS))* carcConst;
 expSS = exp(-distSS/carcDist);
 %expNN = exp(-distNN/carcDist);
 expSN = exp(-distSN/carcDist);

 sumSS = sum(expSS - eye(trApSize));
 %sumNN = sum(expNN - eye(trNoiseSize));
 sumSN = sum(expSN'); % the sum over all noise events  for values from spike cluster
 %sumNS = sum(expSN);  % the sum over all spike events for values from noise cluster

 correctProbS = sumSS ./  (sumSS + sumSN);
 distinction = mean(correctProbS);
 
% disp(['The distinction score for this unit (when all other units, but not plain noise - is considered "noise") is ',mat2str(round(distinction*100)/100)]);
