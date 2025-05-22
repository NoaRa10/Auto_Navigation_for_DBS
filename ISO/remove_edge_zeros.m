function [ analog, apIndex ]  =  remove_edge_zeros(analog, apIndex)

nonZero = find(analog ~=0);
analog = analog(nonZero(1):nonZero(end));
apIndex = apIndex - nonZero(1);
apIndex = apIndex(find( apIndex > 0)) ;
