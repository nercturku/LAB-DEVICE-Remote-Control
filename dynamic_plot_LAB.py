# -*- coding: utf-8 -*-
"""
Created on Fri Oct  7 09:34:33 2022

@author: Maximilien
"""
import matplotlib.pyplot as plt
import numpy as np

plt.ion()
class DynamicUpdate:
    
    min_x = 0
    min_y = 0
    
    # List to be fill for the plot
    
    x_data = []
    y_data = []
    P_data = []
    
    def __init__(self,max_x,max_y):
        
        self.max_x = max_x + 5
        self.max_y = max_y + 1
        self.on_launch()
        
    def on_launch(self):
        #Set up plot
        self.figure, self.ax = plt.subplots()
        self.lines, = self.ax.plot([],[], '-', color = 'blue')
        # Add twin axis for the powercurve
        self.ax_P = self.ax.twinx()
        self.lines_P, = self.ax_P.plot([],[],'-', color = 'yellow')
        #Autoscale on unknown axis and known lims on the other
        #self.ax.set_autoscaley_on(True)
        # Manually scale axis
        
        self.ax.set_xlim(self.min_x, self.max_x)
        self.ax.set_ylim(self.min_y,self.max_y)
        

        self.min_P = self.min_x * self.min_y
        self.max_P = (self.max_y - 1) * (self.max_x - 5)
        self.ax_P.set_ylim(self.min_P,self.max_P)
        
        #Add grid and legend
        self.ax.grid()
        self.ax.set_xlabel('PV Voltage [V]')
        self.ax.set_ylabel('PV Current [A]')
        self.ax_P.set_ylabel('PV Power [P]')
        self.ax_P.legend()
        self.ax.legend((self.lines,self.lines_P),('current','power'))
        
    def on_running(self, xdata, ydata, Pdata):
        
        ## Former points are plot as circles
        if len(xdata)>1:
            #Update data (with the new _and_ the old points)
            self.lines.set_xdata(xdata[:-1])
            self.lines.set_ydata(ydata[:-1])
            self.lines_P.set_xdata(xdata[:-1])
            self.lines_P.set_ydata(Pdata[:-1])
        
        #Need both of these in order to rescale
        self.ax.relim()
        self.ax.autoscale_view()
        self.ax_P.relim()
        self.ax_P.autoscale_view()
        
        ## News points are plot as + marker
        
        self.newlines, = self.ax.plot([],[],'+',color = 'blue',markersize = 12)
        self.newlines_P, = self.ax_P.plot([],[],'+', color = 'yellow',markersize = 12)
        
        self.newlines.set_xdata(xdata[-1])
        self.newlines.set_ydata(ydata[-1])
        self.newlines_P.set_xdata(xdata[-1])
        self.newlines_P.set_ydata(Pdata[-1])
        
        
        
        #We need to draw *and* flush
        
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()
        
        # Following INdications on stackoverflow 
        plt.pause(0.01)
        
        self.newlines.remove()
        self.newlines_P.remove()

        

    
    def add_point(self,x,y):
        """
        Add point of coordinates (x,y) to the plot
        """
        
        self.x_data.append(x)
        self.y_data.append(y)
        self.P_data.append(x*y)
        self.on_running(self.x_data, self.y_data,self.P_data)
        
        return self.x_data, self.y_data,self.P_data
