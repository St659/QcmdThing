import numpy


a = numpy.linspace(0, 20, 30000)
b = numpy.asarray(a)
c = numpy.column_stack(b)
idx = numpy.argmin((c - 11.2)**2)
print(idx)