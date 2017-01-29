from matplotlib import pyplot as plt
from QcmdThing.QCMDExcelReader import QCMDDataReader

filename = 'E:\Chrome Download\Mannose 24-1-17.txt'
reader = QCMDDataReader(filename, '\t')

sensor_data_list = reader.get_sensor_data()

figure = plt.figure()
ax = figure.add_subplot(111)

for sensor in sensor_data_list:
    ax.plot(sensor.time, sensor.d3)


plt.show()