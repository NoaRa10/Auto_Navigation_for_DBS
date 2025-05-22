% knn_test use the k nearest neighbors to estimate the clustering errors 
% IN:  analogAp(N,P) - matrix with the analog signal of the spikes
%         noiseEvents(N,P) - matrix with the analog Signal of the high noise events
%        apSize  -  total number of aps
%         noiseSize - total number of noise events
% OUT : fnErr- estimation of the number of noise events that are missclassified
%           fpErr - estimation of the number of spike events that are missclassified
%          isolation -  scores the difference between the spike events and noise events 
%fnErr is the number of noise events that their most of their knn are from the spike cluster
%             devided by the number of spike events 
%fpErr is the number of spikes that their most of their knn are from the noise cluster
%             devided by the number of spike events 

function [ fnErr, fpErr, isolation] = knn_test(analogAp, noiseEvents)

global TEST_SORT_KNN;  % number of nearest neighbers used in the knn test
global TEST_SORT_CARC_CONST;
global TEST_SORT_PLOT ;
global TEST_SORT_MAX_EVENTS;

error(nargchk(2,2,nargin));
if(size(noiseEvents,1) <2) 
    fnErr =0;
    fpErr =0;
    isolation =1;
    return;
end
if(size(analogAp,1) <2)
    fnErr =1;
    fpErr =0;
    isolation =0;
    return;
end
knn = TEST_SORT_KNN;
carcConst = TEST_SORT_CARC_CONST;

% these are random groups becouse randomization of the order  was performed in get_analog_ap
apTrain = analogAp;

noiseTrain = noiseEvents;

 allTrain = [apTrain ; noiseTrain];
 trApSize = size(apTrain,1);
 trNoiseSize = size(noiseTrain,1);

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
 distNN = sqrt(distMat( (trApSize+1):end,(trApSize+1):end));  
 distSN = sqrt(distMat(1:trApSize, (trApSize+1):end));

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
 isolation = mean(correctProbS);

% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
%  K NEAREST NEIGHBORS  
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% get the k nearest neighbers
[sortAllDist  inx ]  = sort(distMat');

if(knn > trApSize | knn > trNoiseSize  ) %when size of the clusters is less than knn use knn that is 5% of the data
    knn  = min(trNoiseSize, trApSize );
end
firstK = inx(2:(knn+1),:);  % Ignore first row - it is the self distance
% characteristic matrix:  1 for Ap events and -1 for noise events
characMat  = ones(size(firstK));
noiseCharacInx = find(firstK > trApSize);   
characMat(noiseCharacInx) = -1;
% classifier(i) positive -> the i noise event belongs to the noise
%                               negative -> the i noise event is an ap     
classifier = sum(characMat,1);

knnFnNum =  size(find(classifier((trApSize+1):end)  > 0),2 );
knnFpNum  =  size(find(classifier(1:trApSize) < 0),2);  

fnErr = knnFnNum / trApSize;
fpErr = knnFpNum / trApSize;
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% PLOT FEATURES
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

if(TEST_SORT_PLOT)

     [vec score c d] = princomp(allTrain);
    f1Ap =  score(1:trApSize,1);
    f1Noise = score(trApSize+1:end,1);
    f2Ap = score(1:trApSize,2);
    f2Noise = score(trApSize+1:end,2);
    
    plot_features(f1Ap, f2Ap, f1Noise, f2Noise);
    title( ['ap= ' num2str(size(f1Ap,1))   ' noise= '  num2str(size(f1Noise,1))  ]);    
    xlabel('PC1');
    ylabel('PC2');

end