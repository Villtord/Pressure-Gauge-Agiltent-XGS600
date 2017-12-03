#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec  3 14:14:17 2017

Qlabel as digital screen

@author: villtord
"""



from __future__ import unicode_literals
import sys
from Com_port import get_pressure

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QIcon

import numpy
from numpy import sin, arange, pi, interp, linspace


from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class StretchedLabel(QtWidgets.QLabel):
    def __init__(self, *args, **kwargs):
        QtWidgets.QLabel.__init__(self, *args, **kwargs)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

    def resizeEvent(self, evt):
        font = self.font()
        font.setPixelSize(self.height() * 0.8)
        self.setFont(font)



class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, parent=None,  height=1.5, width=3, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111,position=[0.15, 0.15, 0.75, 0.75])
        
#        self.axes.xaxis.set_visible(False) # Hide only x axis
#        self.axes.yaxis.set_visible(False) # Hide only y axis
        self.axes.spines["top"].set_visible(False)
        self.axes.spines["right"].set_visible(False)

        self.compute_initial_figure()

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        pass



class MyDynamicMplCanvas(MyMplCanvas):
    """A canvas that updates itself every second with a new plot."""

    LCD_trigger = QtCore.pyqtSignal(float)

    def __init__(self, *args, **kwargs):
        

        MyMplCanvas.__init__(self, *args, **kwargs)
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.update_figure)
        timer.start(1000)

    def compute_initial_figure(self):
        global length
#        self.axes.plot([i for i in range(1,length+1)], [sin(i*2*pi/length) for i in range(1,length+1)], 'r')
        self.axes.plot(arange(length), [sin(i*2*pi/length) for i in range(1,length+1)], 'r')

    def update_figure(self):
        # Build a list of 4 random integers between 0 and 10 (both inclusive)
        global pressure_table
        global length
        self.com_port_name='COM82'
        self.pressure=get_pressure(self.com_port_name)
        self.pressure=self.pressure.split(",")
        self.pressure_1=float( self.pressure[1])
        pressure_table.append(self.pressure_1)
        if len(pressure_table)>length:
            del pressure_table[0]


        self.LCD_trigger.emit(self.pressure_1)
         
        self.axes.cla()
        self.axes.plot(arange(len(pressure_table)), pressure_table,linestyle='--',marker='o', color='r', markersize=5)

        N=5    
        if len(pressure_table)>N:
            n=int(len(pressure_table)/4)
            cumulative = numpy.cumsum(numpy.insert(pressure_table, 0, 0)) 
            mean_pressure=(cumulative[n:] - cumulative[:-n]) / float(n)
            xvals = linspace(0, len(mean_pressure), len(pressure_table))
            self.axes.plot(arange(len(pressure_table)), interp(xvals, arange(len(mean_pressure)),mean_pressure), 'b')
            
            textstr = '$Mean =%.2f$'"{:.01e}".format(mean_pressure[-1])

            # these are matplotlib.patch.Patch properties
            props = dict(boxstyle='round', facecolor='wheat', alpha=1)

            # place a text box in upper middle in axes coords
            self.axes.text(0.35, 0.95, textstr, transform=self.axes.transAxes, fontsize=14,
            verticalalignment='top', bbox=props)

        self.draw()


class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("application main window")


        self.main_widget = QtWidgets.QWidget(self)

        self.layout = QtWidgets.QVBoxLayout(self.main_widget)

        self.dc = MyDynamicMplCanvas(self.main_widget)
        
#        self.lcdNumber = QtWidgets.QLCDNumber(self.main_widget)
#        self.lcdNumber.setSmallDecimalPoint(True)
#        self.lcdNumber.setDigitCount(7)
#        self.lcdNumber.setStyleSheet("* { background-color: white; color: darkred; }")
#        self.lcdNumber.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
#                                   QtWidgets.QSizePolicy.Expanding)   
#        self.lcdNumber.setMinimumHeight(100)
#        self.layout.addWidget(self.lcdNumber)
        
        self.qtLabel=StretchedLabel(self)
        start_pressure=0.0000000001
        self.qtLabel.setText("{:.01e}".format(start_pressure))
        self.qtLabel.setMinimumHeight(100)
        self.qtLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.qtLabel.setStyleSheet("QLabel { background-color : white; color : red; }")


   
        self.layout.addWidget(self.qtLabel)
        
        
        self.layout.addWidget(self.dc)


        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)
        
        self.dc.LCD_trigger.connect(self.update_LCD)
        
    def update_LCD(self, pressure):

        self.qtLabel.setText("{:.01e}".format(pressure))
#        self.lcdNumber.display(("{:.01e}".format(pressure)))


qApp = QtWidgets.QApplication(sys.argv)
pressure_table=[]
length=100
aw = ApplicationWindow()
aw.setWindowTitle("Preparation Chamber")
aw.show()
sys.exit(qApp.exec_())
qApp.exec_()