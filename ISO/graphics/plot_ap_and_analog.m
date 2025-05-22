%plot ap and anlog in the same graph
function plot_ap_and_analog(analog, apIndex1, apIndex2, first, last, sampleRate) 


base =  std(analog(first:last));
ap1Factor = -6;
ap2Factor = -4;
inx =( first:last)  - first+1; 
inx = inx/ sampleRate;
plot(inx, analog(first:last)); 
hold on
ap = apIndex1(find(apIndex1 > first & apIndex1 < last));
ap = ap-first;
ap = ap/sampleRate;
vals = ones(size(ap)) * base * ap1Factor;
plot( ap, vals,  '*k');

ap = apIndex2(find(apIndex2 > first & apIndex2 < last));
ap = ap-first;
ap = ap/sampleRate;
vals = ones(size(ap)) * base * ap2Factor;
plot(ap,vals, '+r'); 
title('analog signal');
xlabel(' Time(ms)');


hold off

