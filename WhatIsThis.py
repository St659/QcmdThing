
import numpy as np
x=[1,2,3,4,5]
y=[6,7,8,9,10]
points = np.column_stack((x,y))

a = 2.1
b=7.3

print(points - (a,b))
print(((points - (a,b))**2))
print(((points - (a,b))**2).sum(axis=-1))
other = np.nanargmin(points - (a,b))
idx = np.nanargmin(((points - (a,b))**2).sum(axis = 1))

print(idx)
print(other)