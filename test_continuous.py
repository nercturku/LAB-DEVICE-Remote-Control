# -*- coding: utf-8 -*-
"""
Created on Mon Oct 10 16:26:11 2022

@author: Maximilien

TEST Continiuous with the LD400P Load if supply gives according to settings
"""

## IMPORT
import serial
import time
import numpy as np
import matplotlib.pyplot as plt
from dynamic_plot_LAB import DynamicUpdate
from mx180TP import MX180TP_COM

## Configurate matplotlib
plt.ion()

## Connect with MX180TP

COM = "COM4"
MX180TP_connect = MX180TP_COM(COM)
MX180TP_connect.connect()

## PV info
V_oc = 30
FFI = 0.9
FFU = 0.8

compteur = 0
nb_output = 2
I_sc = 5
I_0 = I_sc * (1-FFI)**(1/(1-FFU))
C_AQ = (FFU - 1)/np.log(1-FFI)
plot = DynamicUpdate(V_oc,I_sc)
time.sleep(10)
compteur = 0

## Switching ON the MX180TP

MX180TP_connect.output(nb_output,1)

while compteur < 1000:
    ## Query V
    V_PV = MX180TP_connect.sendAndReceiveCommand("V" + str(nb_output) + "O?")
    
    ## Get the voltage from MX180TP message (string to float)
    V_PV = float(V_PV[:5])
    ## Compute the PV Current according to the Voltage
    I_PV = I_sc - I_0 * (np.exp(V_PV / (V_oc * C_AQ)) - 1)
    
    ## Communicate setpoints to MX180TP
    MX180TP_connect.setup(V_PV, I_PV, nb_output)
    
    ## Display it
    x,y,P = plot.add_point(V_PV,I_PV)
    
    ## Pause of 0.5 seconds
    time.sleep(1)
    compteur += 1
MX180TP_connect.output(nb_output,0)
MX180TP_connect.close()