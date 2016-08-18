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

from __future__ import unicode_literals
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
import threading

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
        # We want the axes cleared every time plot() is called
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


class MyStaticMplCanvas(MyMplCanvas):
    """Simple canvas with a sine plot."""
    def __init__(self, x, harmonics, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)

        self.data_line_list = list()
        self.data_line_num = 0
        self.text_list= list()
        self.harmonics = harmonics
        self.compute_initial_figure(x,self.harmonics[0][:])
        self.overline = False
        self.active = True

    def compute_initial_figure(self,x,f):

        self.plt = self.axes.plot(x, f, gid =0)
        self.plt[0].set_picker(1)
        self.x_array = np.asarray(x)

        self.default_xlim = self.axes.get_xlim()
        self.default_ylim = self.axes.get_ylim()



        self.f_array = np.asarray(f)
        self.points_t = np.column_stack((self.x_array))
        print(self.points_t)
        self.points_s = np.column_stack((self.f_array))

    def onclick(self, event):
        if self.active:
            self.del_line = False
            if event.dblclick:
                self.del_line = True
            if not self.del_line:
                QtCore.QTimer.singleShot(600, lambda: self.check_double_click(event))

    def zoom(self,event):
        # get the current x and y limits
        base_scale = 1.05
        cur_xlim = self.axes.get_xlim()
        cur_ylim = self.axes.get_ylim()
        cur_xrange = (cur_xlim[1] - cur_xlim[0]) * .5
        cur_yrange = (cur_ylim[1] - cur_ylim[0]) * .5
        xdata = event.xdata  # get event x location
        ydata = event.ydata  # get event y location
        if event.button == 'up':
            # deal with zoom in
            scale_factor = 1 / base_scale
        elif event.button == 'down':
            # deal with zoom out
            scale_factor = base_scale
        else:
            # deal with something that should never happen
            scale_factor = 1
            print
            event.button
        # set new limits
        self.axes.set_xlim([xdata - cur_xrange * scale_factor,
                     xdata + cur_xrange * scale_factor])
        self.axes.set_ylim([ydata - cur_yrange * scale_factor,
                     ydata + cur_yrange * scale_factor])
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

    def delete_line(self,event):
        selected_lines = self.axes.get_lines()[1:]
        for index, curve in enumerate(selected_lines):
            print(index)
            if curve.contains(event)[0]:
                print(curve.get_gid())
                del self.axes.lines[index + 1]
                self.data_line_list.pop(index)
                self.data_line_num -= 1
                del self.axes.texts[:]
                self.draw()
        for index, line in enumerate(self.data_line_list):
            self.axes.text(line.xdata[0], line.ydata[0], index + 1)
        self.draw()

    def onmove(self, event):
        try:
            if self.press is not None:
                if self.press:
                    if event.x > self.prevX:
                        print(event.xdata)

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
                    self.setCursor(QtGui.QCursor(QtCore.Qt.ClosedHandCursor))
                    dx = event.xdata - self.xpress
                    dy = event.ydata - self.ypress
                    self.cur_xlim -= dx
                    self.cur_ylim -= dy
                    self.axes.set_xlim(self.cur_xlim)
                    self.axes.set_ylim(self.cur_ylim)
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
        if len(self.axes.lines) > self.data_line_num:
            del self.axes.lines[self.data_line_num]
        self.axes.plot(self.xdata, self.ydata, 'r' , linewidth = 4.0, alpha=0.5, gid = self.data_line_num)
        print("Updated Graph!")
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

class data_line():
    def __init__(self, xdata, harmonics,id):
        self.xdata = xdata
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
        self.setWindowTitle("application main window")

        self.file_menu = QtWidgets.QMenu('&File', self)
        self.file_menu.addAction('&Quit', self.fileQuit,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.menuBar().addMenu(self.file_menu)

        self.button = QtWidgets.QPushButton('Print Data', self)
        self.button.clicked.connect(self.print_selection)

        self.reset_zoom = QtWidgets.QPushButton('Reset Zoom', self)
        self.reset_zoom.clicked.connect(self.zoom_reset)

        self.help_menu = QtWidgets.QMenu('&Help', self)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(self.help_menu)

        self.help_menu.addAction('&About', self.about)

        self.main_widget = QtWidgets.QWidget(self)

        csvfile = open('Book4.csv', newline="")
        reader = csv.reader(csvfile, delimiter =',')
        x = list()
        f3 = list()
        f5 = list()
        f7 = list ()
        f9 = list()
        f11 = list()
        f13 = list()

        for row in reader:
            if len(row)>0:
                try:
                    x.append(float(row[0]))
                    f3.append(float(row[1]))
                    f5.append(float(row[2]))
                    f7.append(float(row[3]))
                    f9.append(float(row[4]))
                    f11.append(float(row[5]))
                    f13.append(float(row[6]))
                except ValueError:
                    pass
        harmonics = [f3, f5,f7,f9,f11,f13]
        self.harmonic_check_box = QtWidgets.QHBoxLayout()

        f3_check = QtWidgets.QCheckBox('F3')
        f5_check = QtWidgets.QCheckBox('F5')
        f7_check = QtWidgets.QCheckBox('F7')
        f9_check = QtWidgets.QCheckBox('F9')
        f11_check = QtWidgets.QCheckBox('F11')
        f13_check = QtWidgets.QCheckBox('F13')

        self.check_list = [f3_check, f5_check, f7_check, f9_check,f11_check,f13_check]

        self.harmonic_check_box.addWidget(f3_check)
        self.harmonic_check_box.addWidget(f5_check)
        self.harmonic_check_box.addWidget(f7_check)
        self.harmonic_check_box.addWidget(f9_check)
        self.harmonic_check_box.addWidget(f11_check)
        self.harmonic_check_box.addWidget(f13_check)

        l = QtWidgets.QVBoxLayout()
        table_vbox = QtWidgets.QVBoxLayout()
        main_box = QtWidgets.QHBoxLayout(self.main_widget)
        self.sc = MyStaticMplCanvas(x, harmonics, self.main_widget, width=5, height=4, dpi=100)
        #dc = MyDynamicMplCanvas(self.main_widget, width=5, height=4, dpi=100)
        l.addWidget(self.sc)
        l.addWidget(self.button)
        l.addWidget(self.reset_zoom)

        self.values = list()
        data = [1,2,3,4,5,6]
        self.values.append(data)
        headers = [['Slope', 'Intercept', 'R value', 'P value', 'K2 ', 'P val Error']]
        self.values_model = DataValuesModel(self.values, headers)
        values_table = DataValuesTableView(self.values_model)

        table_vbox.addLayout(self.harmonic_check_box)
        table_vbox.addWidget(values_table)
        main_box.addLayout(l)
        main_box.addLayout(table_vbox)
        #l.addWidget(dc)

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

        self.statusBar().showMessage("All hail matplotlib!", 2000)

    def print_selection(self):
        del self.values[:]
        data_list = self.sc.get_selected_data()
        harmonic_check = list()

        for box in self.check_list:
            if box.isChecked():
                harmonic_check.append(True)
                print("Box Ticked")
            else:
                harmonic_check.append(False)
                print("Box Not Ticked")

        for data in data_list:
            for harmonic, check in zip(data.harmonics, harmonic_check):
                if check:
                    slope, intercept, r_value, p_value, std_err = stats.linregress(data.xdata, harmonic)

                    line_fit_func = np.vectorize(self.generate_line_fit)
                    line_fit = line_fit_func(data.xdata, slope, intercept)

                    difference = np.subtract(data.harmonics[0], line_fit)
                    k2, p_norm_value = stats.normaltest(difference)
                    rounded = list()
                    float_values = [slope, intercept, r_value, p_value, k2, p_norm_value]
                    for value in float_values:
                        rounded.append(str(round(value,3)))
                    self.values.append(rounded)
        print(self.values)
        self.values_model.set_values(self.values)


    def generate_line_fit(self, x,  slope, intercept):
        y = slope * x + intercept
        return y

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
        self.arraydata[:][:] = values[:][:]
        self.endResetModel()

    def flags(self, index):
        return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.headerdata[0][col]
        return


qApp = QtWidgets.QApplication(sys.argv)

aw = ApplicationWindow()
aw.setWindowTitle("%s" % progname)
aw.show()
sys.exit(qApp.exec_())
qApp.exec_()