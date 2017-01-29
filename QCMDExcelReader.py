from openpyxl import load_workbook
import unittest
import csv
import numpy as np
class QCMDDataReader():
    def __init__(self, filename, delimiter):

        csvfile = open(filename, newline="")
        reader = csv.reader(csvfile, delimiter=delimiter)

        self.qcmd_data_list = list()


        for row in reader:
            if not self.qcmd_data_list:
                self.num_sensors = int(len(row)/15)
                for num in range(self.num_sensors):
                   self.qcmd_data_list.append(QCMDSensorData())
            if len(row) > 0:
                sensors = [row[i:i + 15] for i in range(0, len(row), 15)]
                for index, sensor in enumerate(sensors):
                    try:
                        self.save_qcmd_data(index,sensor)
                    except ValueError:
                        pass
        self.normalise_qcmd_data()

    def save_qcmd_data(self, index, sensor):
        qcmd_data = self.qcmd_data_list[index].get_values()

        for data_list, value in zip(qcmd_data, sensor):
            data_list.append(float(value))

    def normalise_qcmd_data(self):
        for sensor in self.qcmd_data_list:
            qcmd_data = sensor.get_values()[1:]
            for data in qcmd_data:
                zero = data[0]
                data[:] = [x - zero for x in data]

    def get_sensor_data(self):
        return self.qcmd_data_list


class QCMDSensorData():
    def __init__(self):
        self.time = list()
        self.f1 = list()
        self.f3 = list()
        self.f5 = list()
        self.f7 = list()
        self.f9 = list()
        self.f11 = list()
        self.f13 = list()

        self.d1 = list()
        self.d3 = list()
        self.d5 = list()
        self.d7 = list()
        self.d9 = list()
        self.d11 = list()
        self.d13 = list()

    def get_values(self):
        return [self.time, self.f1, self.d1, self.f3, self.d3, self.f5, self.d5, self.f7, self.d7,
                    self.f9, self.d9, self.d11, self.f13, self.d13]


class TestQCMDDataReader(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        filename = 'E:\Chrome Download\Mannose 24-1-17.txt'
        self.reader = QCMDDataReader(filename, '\t')

    def test_num_sensors(self):
        self.assertEqual(self.reader.num_sensors, 2)

    def test_qcmd_data_list_size(self):
        self.assertEqual(len(self.reader.qcmd_data_list),2)

    #def test_get_time(self):
     #   self.assertEqual(self.reader.get_time()[0], 0.34)
