#!/usr/bin/env python

# embedding_in_qt5.py --- Simple Qt5 application embedding matplotlib canvases
#
# Copyright (C) 2005 Florent Rougon
#               2006 Darren Dale
#               2015 Jens H Nielsen
#
# This file is an example program for matplotlib. It may be used and
# modified with no restriction; raw copies as well as modified versions
# may be distributed without limitation.

#from __future__ import unicode_literals
import sys
import os
import random
import matplotlib
# Make sure that we are using QT5
matplotlib.use('Qt5Agg')
from PyQt5 import QtCore, QtWidgets, QtGui


from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from scipy import stats
import csv
import unittest
import random
import string


progname = os.path.basename(sys.argv[0])
progversion = "0.1"


class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.press = None
        self.prevX = 0
        self.ydata = list()
        self.xdata = list()
        fig = Figure(figsize=(width, height), dpi=dpi)

        self.axes = fig.add_subplot(111)

        self.axes.hold(True)

        #self.compute_initial_figure()

        #
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        FigureCanvas.mpl_connect(self,'button_press_event', self.onclick)
        FigureCanvas.mpl_connect(self, 'button_release_event', self.onrelease)
        FigureCanvas.mpl_connect(self, 'motion_notify_event', self.onmove)
        FigureCanvas.mpl_connect(self, 'scroll_event', self.zoom)
        FigureCanvas.mpl_connect(self, 'pick_event', self.onpick)
        FigureCanvas.mpl_connect(self, 'figure_enter_event', self.on_enter)
        FigureCanvas.mpl_connect(self, 'figure_exit_event', self.on_exit)

    def compute_initial_figure(self):
        pass

    def onclick(self,event):
        pass

    def onpick(self,event):
        pass

    def onmove(self,event):
        pass

    def onrelease(self, event):
        pass

    def scroll(self,event):
        pass

    def on_enter(self,event):
        pass

    def on_exit(self,event):
        pass


class QCMDDataPlotter(MyMplCanvas):
    """Simple canvas with a sine plot."""
    def __init__(self,  *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)

        self.data_line_list = list()
        self.data_line_num = 0
        self.text_list= list()

        self.harmonics = []
        self.overline = False
        self.active = True

    def compute_initial_figure(self,x,harmonics, check_values):
        self.harmonics = harmonics
        self.time = x
        self.check_values = check_values

        for plot_harmonic, harmonic in zip(check_values,harmonics):
            if plot_harmonic:
                self.plt = self.axes.plot(x, harmonic)
        self.plt[0].set_picker(1)
        self.x_array = np.asarray(x)

        self.default_xlim = self.axes.get_xlim()
        self.default_ylim = self.axes.get_ylim()
        self.prev_xlim = self.default_xlim


        self.f_array = np.asarray(self.harmonics[0][:])
        self.points_t = np.column_stack((self.x_array))
        self.points_s = np.column_stack((self.f_array))
        self.draw()



    #Used to update the displayed harmonics when graph has been created
    def redraw_harmonics(self, check_values):
        self.axes.cla()
        self.check_values = check_values
        for plot_harmonic, harmonic in zip(check_values, self.harmonics):
            if plot_harmonic:
                self.plt = self.axes.plot(self.time, harmonic)
        line_nums = range(1, len(self.data_line_list) + 1, 1)
        for line, line_num in zip(self.data_line_list, line_nums):
            line.id = line_num
            self.axes.plot(line.xdata, line.ydata, 'r', linewidth=6.0, alpha=0.7, gid = line.id)
            self.axes.text(line.xdata[0], line.ydata[0], str(line.id))
        self.draw()

    def clear_figure(self):
        self.axes.cla()
        self.data_line_list= list()

        self.data_line_num = 0
        self.text_list = list()


    def onclick(self, event):
        if self.active:
            self.del_line = False
            if event.dblclick:
                self.del_line = True
            if not self.del_line:
                QtCore.QTimer.singleShot(500, lambda: self.check_double_click(event))

    def zoom(self,event):
        # get the current x and y limits
        base_scale = 1.01
        cur_xlim = self.axes.get_xlim()
        cur_ylim = self.axes.get_ylim()

        if event.button == 'up':
            # deal with zoom in
            self.axes.set_xlim([cur_xlim[0] + base_scale,
                                cur_xlim[1] - base_scale])
            self.axes.set_ylim([cur_ylim[0] + base_scale,
                                cur_ylim[1] - base_scale])
        elif event.button == 'down':
            # deal with zoom out
            self.axes.set_xlim([cur_xlim[0] - base_scale,
                                cur_xlim[1] + base_scale])
            self.axes.set_ylim([cur_ylim[0] - base_scale,
                                cur_ylim[1] + base_scale])
        else:
            # deal with something that should never happen
            scale_factor = 1

            event.button
        # set new limits

        self.draw()  # force re-draw

    def reset_zoom(self):
        self.axes.set_xlim([self.default_xlim[0],self.default_xlim[1]])

        self.axes.set_ylim([self.default_ylim[0],self.default_ylim[1]])
        self.draw()


    def check_double_click(self, event):
        if self.del_line:
            self.delete_line(event)
        else:
            if self.overline:
                self.press = True
                self.initialx = event.xdata
                self.prevX = 0
                self.data_line_num += 1
            else:
                self.press = False
                self.cur_xlim = self.axes.get_xlim()
                self.cur_ylim = self.axes.get_ylim()
                self.xpress = event.xdata
                self.ypress = event.ydata
                self.setCursor(QtGui.QCursor(QtCore.Qt.ClosedHandCursor))

    def delete_line(self,event):
        num_harmonics = [x for x in self.check_values if x is not False]

        selected_lines = self.axes.get_lines()[len(num_harmonics):]

        for index, curve in enumerate(selected_lines):

            if curve.contains(event)[0]:
                print(curve.get_gid())

                [self.data_line_list.pop(line_num.id -1) for line_num in self.data_line_list if line_num.id == curve.get_gid()]
                self.data_line_num -= 1

                self.redraw_harmonics(self.check_values)

        self.draw()

    def onmove(self, event):
        try:
            if self.press is not None:
                if self.press:
                    if event.x > self.prevX:


                        idx = np.argmin((self.points_t - (event.xdata)) ** 2)

                        self.xdata.append(self.points_t[0][idx])
                        self.ydata.append(self.points_s[0][idx])
                        self.update_graph(event)
                    elif self.initialx < event.x < self.prevX:
                        try:
                            self.xdata.pop()
                            self.ydata.pop()
                        except IndexError:
                            return
                        self.update_graph(event)
                else:

                    dx = event.xdata - self.xpress
                    dy = event.ydata - self.ypress
                    self.cur_xlim -= dx
                    self.cur_ylim -= dy
                    if self.cur_xlim[1] > self.default_xlim[1] or self.cur_xlim[0] < self.default_xlim[0] or \
                                    self.cur_ylim[1]> (self.default_ylim[1] +10) or self.cur_ylim[0]< (self.default_ylim[0] - 10):
                        pass
                    else:
                        self.axes.set_xlim(self.cur_xlim)
                        self.axes.set_ylim(self.cur_ylim)
                        self.prev_xlim = self.cur_xlim
                    self.draw()

            else:
                for curve in self.axes.get_lines():
                    if curve.contains(event)[0]:
                        self.setCursor(QtGui.QCursor(QtCore.Qt.IBeamCursor))
                        self.overline = True
                        break
                    else:
                        self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
                        self.overline =False

        except TypeError:
            pass

    def onrelease(self, event):
        if self.press:

            if len(self.xdata) > 0:
                self.axes.text(self.xdata[0], self.ydata[0], str(self.data_line_num))

                self.data_line_list.append(data_line(self.xdata[:], self.ydata[:], self.data_line_num))
            else:
                self.data_line_num -= 1
            del self.xdata[:]
            del self.ydata[:]
            self.draw()
        self.press = None

    def update_graph(self, event):
        self.redraw_harmonics(self.check_values)
        self.axes.plot(self.xdata, self.ydata, 'r' , linewidth = 6.0, alpha=0.7, gid = self.data_line_num)


        self.draw()
        self.prevX = event.x

    def get_selected_data(self):
        for data in self.data_line_list:
            idx_start = np.argmin((self.points_t - (data.xdata[0])) ** 2)
            idx_end = np.argmin((self.points_t - (data.xdata[-1])) ** 2)
            fulldata_x = self.x_array[idx_start:idx_end]
            f3 = self.f_array[idx_start:idx_end]
            #Get values for harmonics
            f5 = np.asarray(self.harmonics[1][idx_start:idx_end])
            f7 = np.asarray(self.harmonics[2][idx_start:idx_end])
            f9 = np.asarray(self.harmonics[3][idx_start:idx_end])
            f11 = np.asarray(self.harmonics[4][idx_start:idx_end])
            f13 = np.asarray(self.harmonics[5][idx_start:idx_end])

            full_harm = [f3,f5,f7,f7,f9,f11,f3]
            data.xdata[:] = fulldata_x[:]
            data.harmonics= full_harm

        return self.data_line_list

    def on_enter(self,event):
        self.active = True

    def on_exit(self,event):
        self.active = False

    def clear_figure(self):
        self.axes.cla()

class data_line():
    def __init__(self, xdata, harmonics,id):
        self.xdata = xdata
        self.ydata = harmonics
        self.harmonics = harmonics
        self.id = id

class MyDynamicMplCanvas(MyMplCanvas):
    """A canvas that updates itself every second with a new plot."""

    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.update_figure)
        timer.start(1000)

    def compute_initial_figure(self):
        self.axes.plot([0, 1, 2, 3], [1, 2, 0, 4], 'r')

    def update_figure(self):
        # Build a list of 4 random integers between 0 and 10 (both inclusive)
        l = [random.randint(0, 10) for i in range(4)]

        self.axes.plot([0, 1, 2, 3], l, 'r')
        self.draw()


class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("QCMD Data Analyser")

        self.file_menu = QtWidgets.QMenu('&File', self)
        self.file_menu.addAction('Open', self.file_open)
        self.file_menu.addAction('&Quit', self.fileQuit,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)

        self.menuBar().addMenu(self.file_menu)

        self.button = QtWidgets.QPushButton('Fit Selected Data', self)
        self.button.clicked.connect(self.print_selection)
        self.export_button = QtWidgets.QPushButton('Export CSV', self)
        self.export_button.clicked.connect(self.export_csv)

        self.reset_zoom = QtWidgets.QPushButton('Reset Zoom', self)
        self.reset_zoom.clicked.connect(self.zoom_reset)

        self.help_menu = QtWidgets.QMenu('&Help', self)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(self.help_menu)

        self.help_menu.addAction('&About', self.about)

        self.main_widget = QtWidgets.QWidget(self)


        tab = QtWidgets.QTabWidget()
        self.l = QtWidgets.QVBoxLayout()
        table_vbox = QtWidgets.QVBoxLayout()
        main_box = QtWidgets.QHBoxLayout(self.main_widget)
        self.freq_graph = QCMDGraphTableLayout(self.main_widget)
        self.diss_graph = QCMDGraphTableLayout(self.main_widget)
        tab.addTab(self.freq_graph, "Frequency")
        tab.addTab(self.diss_graph, "Dissipation")
        self.graph_selection_box = GraphHarmonicSelectionBox(self.freq_graph, self.diss_graph)
        self.harmonic_check_box = HarmonicSelectionBox()
        self.l.addWidget(tab)

        #dc = MyDynamicMplCanvas(self.main_widget, width=5, height=4, dpi=100)
        #l.addWidget(self.sc)
        self.l.addWidget(self.graph_selection_box)
        self.l.addWidget(self.button)
        self.l.addWidget(self.reset_zoom)


        self.values = list()
        self.initial_table_values = [" "," "," "," "," "," "]
        self.values.append(self.initial_table_values)
        self.headers = [['ID ','Slope', 'Intercept', 'R value', 'P value', 'K2 ', 'P val Error']]
        self.values_model = DataValuesModel(self.values, self.headers)
        values_table = DataValuesTableView(self.values_model)

        self.l.addWidget(self.harmonic_check_box)

        self.l.addWidget(self.export_button)
        main_box.addLayout(self.l)

        #l.addWidget(dc)
        self.statusBar().showMessage("Welcome to QCMD Data Analyser", 4000)
        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)



    def file_open(self):

        file_dialog = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', '.')
        filename = ''.join(file_dialog)

        reader = QCMDDataReader(filename)
        self.freq_graph.clear_figure()
        self.diss_graph.clear_figure()
        harmonics = self.graph_selection_box.get_checkboxes_values()
        self.freq_graph.initialise_graph(reader.get_time(), reader.get_harmonics(), harmonics)
        self.diss_graph.initialise_graph(reader.get_time(), reader.get_dissapation(),harmonics)
        self.values = list()
        self.values.append(self.initial_table_values)
        self.values_model.set_values(self.values)


    def print_selection(self):
        self.diss_graph.fit_selected_values(self.harmonic_check_box.get_checkboxes_values())
        self.freq_graph.fit_selected_values(self.harmonic_check_box.get_checkboxes_values())


    def export_csv(self):

        file_dialog = QtWidgets.QFileDialog.getSaveFileName(self, 'Save file','.', '.csv')
        filename =''.join(file_dialog)
        freq_values = self.freq_graph.get_fit_results()
        diss_values = self.diss_graph.get_fit_results()
        try:
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile, delimiter=',')
                writer.writerow()
                for line in freq_values:
                    writer.writerow(line)
                writer.writerow("")
                writer.writerow(self.headers[0])
                for line in diss_values:
                    writer.writerow(line)
                self.statusBar().showMessage("File Saved!", 4000)
        except FileNotFoundError:
            print("File not found")





    def zoom_reset(self):
        self.sc.reset_zoom()

    def fileQuit(self):
        self.close()

    def closeEvent(self, ce):
        self.fileQuit()

    def about(self):
        QtWidgets.QMessageBox.about(self, "About",
                                    """embedding_in_qt5.py example
Copyright 2005 Florent Rougon, 2006 Darren Dale, 2015 Jens H Nielsen

This program is a simple example of a Qt5 application embedding matplotlib
canvases.

It may be used and modified with no restriction; raw copies as well as
modified versions may be distributed without limitation.

This is modified from the embedding in qt4 example to show the difference
between qt4 and qt5"""
                                )

class QCMDGraphTableLayout(QtWidgets.QWidget):
    def __init__(self, main_widget):
        super(QCMDGraphTableLayout, self).__init__()
        hbox = QtWidgets.QHBoxLayout()
        self.graph = QCMDDataPlotter(main_widget, width=5, height=4,
                                  dpi=100)
        self.values = list()
        self.initial_table_values = [" ", " ", " ", " ", " ", " "]
        self.values.append(self.initial_table_values)
        self.headers = [['ID ', 'Slope', 'Intercept', 'R value', 'P value', 'K2 ', 'P val Error']]
        self.values_model = DataValuesModel(self.values, self.headers)
        self.values_table = DataValuesTableView(self.values_model)

        self.values_table.setMinimumWidth(500)
        self.values_table.resizeColumnsToContents()
        self.values_table.horizontalHeader().setStretchLastSection(True)



        hbox.addWidget(self.graph)
        hbox.addWidget(self.values_table)
        self.setLayout(hbox)

    def get_graph(self):
        return self.graph

    def clear_figure(self):
        self.graph.clear_figure()

    def initialise_graph(self,time, harmonics, check_values):
        self.graph.compute_initial_figure(time, harmonics, check_values)


    def update_graph(self,check_values):
        self.graph.redraw_harmonics(check_values)

    def fit_selected_values(self, harmonic_check):
        data_list = self.graph.get_selected_data()

        if not data_list:
           return
        else:

            self.fit_values = self.calculate_values(data_list, harmonic_check)
            self.values_model.set_values(self.fit_values)
            self.values_table.resizeColumnsToContents()


    def calculate_values(self, data_list, harmonic_check):
        values = list()
        for index, data in enumerate(data_list):
            for harmonic, check in zip(data.harmonics, harmonic_check):
                if check:
                    slope, intercept, r_value, p_value, std_err = stats.linregress(data.xdata, harmonic)

                    line_fit_func = np.vectorize(self.generate_line_fit)
                    line_fit = line_fit_func(data.xdata, slope, intercept)

                    difference = np.subtract(data.harmonics[0], line_fit)
                    k2, p_norm_value = stats.normaltest(difference)
                    rounded = list()
                    id = check + " " + str(index + 1)
                    rounded.append(id)
                    float_values = [slope, intercept, r_value, p_value, k2, p_norm_value]
                    for value in float_values:
                        rounded.append(str(round(value, 3)))
                    values.append(rounded)
        return values

    def generate_line_fit(self, x, slope, intercept):
        y = slope * x + intercept
        return y
    def get_fit_results(self):
        return self.fit_values


class QCMDDataReader():
    def __init__(self, filename):

        csvfile = open(filename, newline="")
        reader = csv.reader(csvfile, delimiter=',')
        self.time = list()
        f3 = list()
        f5 = list()
        f7 = list()
        f9 = list()
        f11 = list()
        f13 = list()
        d3 = list()
        d5 =list()
        d7 = list()
        d9= list()
        d11 = list()
        d13 = list()

        for row in reader:
            if len(row) > 0:
                try:
                    self.time.append(float(row[0]))
                    f3.append(float(row[1]))
                    f5.append(float(row[2]))
                    f7.append(float(row[3]))
                    f9.append(float(row[4]))
                    f11.append(float(row[5]))
                    f13.append(float(row[6]))
                    d3.append(float(row[7]))
                    d5.append(float(row[8]))
                    d7.append(float(row[9]))
                    d9.append(float(row[10]))
                    d11.append(float(row[11]))
                    d13.append(float(row[12]))

                except ValueError:
                    pass
        self.harmonics = [f3, f5, f7, f9, f11, f13]
        self.dissapation = [d3,d5,d7,d9,d11,d13]

    def get_harmonics(self):
        return self.harmonics

    def get_dissapation(self):
        return self.dissapation

    def get_time(self):
        return self.time



class HarmonicSelectionBox(QtWidgets.QGroupBox):
    def __init__(self):
        super(HarmonicSelectionBox, self).__init__()
        f3_check = QtWidgets.QCheckBox('F3')
        f3_check.setChecked(True)
        f5_check = QtWidgets.QCheckBox('F5')
        f7_check = QtWidgets.QCheckBox('F7')
        f9_check = QtWidgets.QCheckBox('F9')
        f11_check = QtWidgets.QCheckBox('F11')
        f13_check = QtWidgets.QCheckBox('F13')

        self.check_list = [f3_check, f5_check, f7_check, f9_check, f11_check, f13_check]

        self.setTitle("Fit Harmonics")

        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(f3_check)
        hbox.addWidget(f5_check)
        hbox.addWidget(f7_check)
        hbox.addWidget(f9_check)
        hbox.addWidget(f11_check)
        hbox.addWidget(f13_check)

        self.setLayout(hbox)

    def get_checkbox_list(self):
        return self.check_list

    def get_checkboxes_values(self):
        harmonic_check = list()
        for box in self.check_list:
            if box.isChecked():
                harmonic_check.append(box.text())
            else:
                harmonic_check.append(False)
        return harmonic_check

class GraphHarmonicSelectionBox(HarmonicSelectionBox):
    def __init__(self, freq_graph, diss_graph):
        super(GraphHarmonicSelectionBox, self).__init__()
        self.setTitle("Plot Harmonic")
        self.freq_graph = freq_graph
        self.diss_graph = diss_graph
        for box in self.check_list:
            box.stateChanged.connect(self.set_plot_harmonics)

    def set_plot_harmonics(self):
        self.freq_graph.update_graph(self.get_checkboxes_values())
        self.diss_graph.update_graph(self.get_checkboxes_values())



class DataValuesTableView(QtWidgets.QTableView):
    def __init__(self, model):
        QtWidgets.QTableView.__init__(self)
        self.setModel(model)

        # set the minimum size
        self.setMinimumSize(400, 300)

        # hide grid
        self.setShowGrid(False)

        # set the font
        font = QtGui.QFont("Courier New", 8)
        self.setFont(font)

        # hide vertical header
        #vh = self.verticalHeader()
        #vh.setVisible(True)

        # set horizontal header properties
        hh = self.horizontalHeader()
        # hh.setStretchLastSection(True)

        # set column width to fit contents
        #self.resizeColumnsToContents()

class DataValuesModel(QtCore.QAbstractTableModel):
    def __init__(self, datain, headerdata, parent=None, *args):
        """ datain: a list of lists
            headerdata: a list of strings
        """
        QtCore.QAbstractTableModel.__init__(self, parent, *args)
        self.arraydata = datain
        self.headerdata = headerdata

    def rowCount(self, parent):
        return len(self.arraydata)

    def columnCount(self, parent):
        return len(self.arraydata[0])

    def data(self, index, role):
        if not index.isValid():
            return None
        elif role != QtCore.Qt.DisplayRole:
            return None
        return self.arraydata[index.row()][index.column()]

    def set_values(self, values):
        # The str() cast is because we don't want to be storing a Qt type in here.
        self.beginResetModel()
        self.arraydata = values[:][:]
        self.endResetModel()

    def flags(self, index):
        return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.headerdata[0][col]
        return


class TestQCMDDataReader(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.reader = QCMDDataReader('Book4.csv')

    def test_time_length(self):
        self.assertEqual(len(self.reader.get_time()), 30983)

    def test_time_values(self):
        time = self.reader.get_time()
        self.assertEqual(time[0],-0.59982)
        self.assertEqual(time[-1], 19.31301)

    def test_harmonics_length(self):
        self.assertEqual(len(self.reader.get_harmonics()),6)

    def test_harmonic_values(self):
        harmonic3 = self.reader.get_harmonics()[0]
        self.assertEqual(harmonic3[0],29.39353)
        self.assertEqual(harmonic3[-1], 23.21427)

    def test_dissapation_length(self):
        self.assertEqual(len(self.reader.get_dissapation()),6)

    def test_dissapation_values(self):
        diss = self.reader.get_dissapation()[0]
        self.assertEqual(diss[0],-10.17701)
        self.assertEqual(diss[-1], -12.68919)

if __name__ == "__main__":
    qApp = QtWidgets.QApplication(sys.argv)

    aw = ApplicationWindow()

    aw.show()
    sys.exit(qApp.exec_())
    qApp.exec_()