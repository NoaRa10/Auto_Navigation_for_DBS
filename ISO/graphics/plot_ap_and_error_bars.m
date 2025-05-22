% plot the mean ap and the sd error bars
function plot_ap_and_error_bars(apMean, apSD)
% plot mean ap with error bars
plot(apMean, 'b');
hold on
barInx = 1:4:size(apMean,2);
errorbar(barInx, apMean(barInx), apSD(barInx), 'r.' );
hold off