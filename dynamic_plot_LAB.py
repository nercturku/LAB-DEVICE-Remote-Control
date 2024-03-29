# -*- coding: utf-8 -*-
"""
Created on Fri Oct  7 09:34:33 2022

@author: Maximilien

Stack overflow weblink where the main idea come from :
    https://stackoverflow.com/questions/10944621/dynamically-updating-plot-in-matplotlib

Activate dynamic plot on Spyder 
    --> Tools tabs --> preferences --> Ipython console --> Graphics --> Backend --> Automatic
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
    eff_data = []
    irr_data = []
    
    def __init__(self,max_x,max_y, minute):
        
        self.max_x = max_x + 5
        self.max_y = max_y + 1
        self.minute = minute
        self.on_launch()
        
    def on_launch(self):
        #Set up 1st subplot --> historic of what is happening
        self.figure, (self.ax,self.ax_2) = plt.subplots(nrows = 2)
        self.lines, = self.ax.plot([],[], '-', color = 'blue')
        # Add twin axis for the powercurve
        self.ax_P = self.ax.twinx()
        self.lines_P, = self.ax_P.plot([],[],'-', color = 'red')
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
        self.ax_P.set_ylabel('PV Power [W]')
        self.ax_P.legend()
        self.ax.legend((self.lines,self.lines_P),('current','power'))
        
        ## Set up 2nd subplot --> Current PV (V / I) points on the I-V curve
        
        self.lines_2, = self.ax_2.plot([],[],'-',color = 'blue')
        # Add twin axis for the powercurve
        self.ax_2_P = self.ax_2.twinx()
        self.lines_2_P, = self.ax_2_P.plot([],[],'-',color = 'red')
        
         # Manually scale axis
        
        self.ax_2.set_xlim(self.min_x, self.max_x)
        self.ax_2.set_ylim(self.min_y,self.max_y)
        

        self.min_P = self.min_x * self.min_y
        self.max_P = (self.max_y - 1) * (self.max_x - 5)
        self.ax_2_P.set_ylim(self.min_P,self.max_P)
        
        #Add grid and legend
        self.ax_2.grid()
        self.ax_2.set_xlabel('PV Voltage [V]')
        self.ax_2.set_ylabel('PV Current [A]')
        self.ax_2_P.set_ylabel('PV Power [W]')
        self.ax_2_P.legend()
        self.ax_2.legend((self.lines_2,self.lines_2_P),('current','power'))
        plt.tight_layout()
        
        ## Set up the second Figure with the efficiency + irradiance plot according to time
        self.figure_eta, (self.ax_eta, self.ax_irr) = plt.subplots(nrows = 2)
        self.lines_eta, = self.ax_eta.plot([],[], '-', color = 'blue')
        self.ax_eta.set_xlim(0, self.minute * 60)
        self.ax_eta.set_ylim(0, 1.1)
        
        self.ax_eta.set_xlabel('Time [s]')
        self.ax_eta.set_ylabel('Eff [%]')
        
        
        self.lines_irr, = self.ax_irr.plot([],[],'-',color = 'blue')
        self.ax_irr.set_xlim(0, self.minute * 60)
        self.ax_irr.set_ylim(0, 1200)
        
        self.ax_irr.set_xlabel('Time [s]')
        self.ax_irr.set_ylabel('Irradiance [W/m2]')
        plt.tight_layout()
        
    def on_running(self, xdata, ydata, Pdata, V_PV_array, I_PV_array,P_PV_array, eff_data, irr_data):
        
        ## Former points are plot
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
        
        self.newlines, = self.ax.plot([],[],'+',color = 'blue',markersize = 20)
        self.newlines_P, = self.ax_P.plot([],[],'+', color = 'red',markersize = 20)
        
        self.newlines.set_xdata(xdata[-1])
        self.newlines.set_ydata(ydata[-1])
        self.newlines_P.set_xdata(xdata[-1])
        self.newlines_P.set_ydata(Pdata[-1])
        
        ## 2nd plot : I-V curve Characteristics  + the current point

        ## News points are plot as + marker
        
        self.newlines_2, = self.ax_2.plot([],[],'+',color = 'blue',markersize = 20)
        self.newlines_2_P, = self.ax_2_P.plot([],[],'+', color = 'red',markersize = 20)
        
        self.newlines_2.set_xdata(xdata[-1])
        self.newlines_2.set_ydata(ydata[-1])
        self.newlines_2_P.set_xdata(xdata[-1])
        self.newlines_2_P.set_ydata(Pdata[-1])
        
        ## Plot the I-V curve corresponding to the V_PV / I_PV
        
        self.lines_2, = self.ax_2.plot(V_PV_array, I_PV_array, '-',color = 'blue')
        

        self.lines_2_P, = self.ax_2_P.plot(V_PV_array, P_PV_array, '-', color = 'red')
        
        
        
        ## 2nd figure --> Plot the Efficiency and the irradiance
        ## Former points are plot
        if len(eff_data)>1:
            #Update data (with the new _and_ the old points)
            self.lines_eta.set_xdata([i for i in range(len(eff_data[:-1]))])
            self.lines_eta.set_ydata(eff_data[:-1])
            self.lines_irr.set_xdata([i for i in range(len(irr_data[:-1]))])
            self.lines_irr.set_ydata(irr_data[:-1])
            
        #Need both of these in order to rescale
        self.ax_eta.relim()
        self.ax_eta.autoscale_view()
        self.ax_irr.relim()
        self.ax_irr.autoscale_view()
        
        ## News points are plot as + marker
        
        self.newlines_eta, = self.ax_eta.plot([],[],'+',color = 'blue',markersize = 20)
        self.newlines_irr, = self.ax_irr.plot([],[],'+', color = 'blue',markersize = 20)
        
        self.newlines_eta.set_xdata([len(eff_data)])
        self.newlines_eta.set_ydata([eff_data[-1]])
        self.newlines_irr.set_xdata([len(irr_data)])
        self.newlines_irr.set_ydata([irr_data[-1]])
        # We need to draw *and* flush on second plot
        
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()
        
        self.figure_eta.canvas.draw()
        self.figure_eta.canvas.flush_events()
        
        # Following Indications on stackoverflow  --> remove former marker
        plt.pause(0.01)
        
        self.newlines_2.remove()
        self.newlines_2_P.remove()
        self.lines_2.remove()
        self.lines_2_P.remove()

        
        self.newlines.remove()
        self.newlines_P.remove()
        self.newlines_eta.remove()
        self.newlines_irr.remove()
        
    def add_point(self,x,y,V_PV_array,I_PV_array, P_PV_array, eff, irr):
        """
        Add point of coordinates (x,y) to the plot
        """
        
        self.x_data.append(x)
        self.y_data.append(y)
        self.P_data.append(x*y)
        self.eff_data.append(eff)
        self.irr_data.append(irr)
        self.on_running(self.x_data, self.y_data,self.P_data,
                        V_PV_array,I_PV_array,P_PV_array, self.eff_data, self.irr_data)
        
        return self.x_data, self.y_data,self.P_data,P_PV_array
