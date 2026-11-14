function result = sum_calculation()
    sum1 = sum((1:50).^2);  
    sum2 = sum(1./(1:10));  
    result = sum1 + sum2;
    fprintf('结果为: %.4f\n', result);
end