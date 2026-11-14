function result = factorial_sum(t)
    sum_factorial = 0;
    for k = 1:t
        sum_factorial = sum_factorial + factorial(k);
    end
    result = sum_factorial;
    
    if nargin > 0
        expression_value = result;  
        fprintf('当t=%d时，表达式的值为: %.4f\n', t, expression_value);
    end
end
