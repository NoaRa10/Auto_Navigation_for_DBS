% concat all noise traces - traces that did not pass threshold 

function [ noise ] = get_analog_noise(analog, apIndex,  maxSteps)
global binSize splitRate;
noiseIndex = 1;
noise  = [];
for i =1:maxSteps 
    if(apIndex(i) > noiseIndex) % could happen if the 2 aps are closer than binSize
        noise =  [ noise analog(noiseIndex:apIndex(i)-binSize)];
    end
    noiseIndex = apIndex(i) + binSize;
end
noise = jitter_cancelation(noise);


