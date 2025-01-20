import numpy as np
import scipy.stats as stats

def generate_data(size, shape=None):
    if shape:
        data = stats.weibull_min(shape).rvs(size)
    else:
        data = np.random.normal(size=size)
    return data

size = 1000
shape_parameter = 1.5  # Set to None to use default distribution
data = generate_data(size, shape_parameter)

print(data)