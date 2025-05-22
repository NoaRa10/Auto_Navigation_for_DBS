% plot the features on the 2 dimension graph - each point is a event

function plot_features(cluster1F1, cluster1F2, cluster2F1, cluster2F2) 
global PLOT_FEATURE_HANDLER;
global PLOT_FEATURE_CURR_ROW;
global PLOT_FEATURE_MAX_ROWS;
if(isempty( PLOT_FEATURE_HANDLER)   | PLOT_FEATURE_CURR_ROW  >   PLOT_FEATURE_MAX_ROWS)
    PLOT_FEATURE_CURR_ROW  =1;
    PLOT_FEATURE_HANDLER  =figure ;
end
figure( PLOT_FEATURE_HANDLER  );
curr = 2 *(PLOT_FEATURE_CURR_ROW -1) +1;
max = PLOT_FEATURE_MAX_ROWS;
subplot(max,2, curr), plot( cluster1F1, cluster1F2 , '.b',cluster2F1, cluster2F2 , '.r') ;
subplot(max,2,curr+1),plot( cluster2F1, cluster2F2 , '.r',cluster1F1, cluster1F2 , '.b') ;
PLOT_FEATURE_CURR_ROW = PLOT_FEATURE_CURR_ROW +1;

