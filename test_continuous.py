# -*- coding: utf-8 -*-
"""
Created on Mon Oct 10 16:26:11 2022

@author: Maximilien

TEST Continiuous with the LD400P Load if supply gives according to settings

MPPT Trial

"""

## IMPORT
import time
import numpy as np
import matplotlib.pyplot as plt
from dynamic_plot_LAB import DynamicUpdate
from mx180TP import mode,Communication,MX180TP, LD400P


def MPPT_LD400P(I_init,load_com,supply_com,dynamic_plot):
    """
    Performs MPPT between a LD400P DC load and a MX180TP DC supply
    
    load_com is the objected connected with LD400P
    supply_com is the object connected with MX180TP
    
    """
    def I_sc_fct(G,I_sc_stc):
        """
        
        Compute the short circuit current of the simulated PV panel
        according to irradiance level [W/m²]
        I_sc_stc : short circuit current in standard test conditions
        """
        return I_sc_stc * (G / 1000)
    
    def V_oc_fct(G,V_oc_stc,CV = 8.593e-2,CR = 1.088e-4,CG = 2.514e-3):
        """
        Parameters
        ----------
        G : Float
            irrandiance [W/m²]
        V_oc_stc : Float
            Open circuit Voltage [V]
        CV,CR,CG : Float, optional
            Techonology correction Factor. 
            The default is 8.593e-2, 1.088e-4, 2.514e-3 respectively.
        Returns
        -------
        V_oc : Open circuit voltage [V] according to irradiance
        """
        return V_oc_stc * (np.log(1 + G/CG)*CV - CR * G)
    
    def irradiance(compteur):
        """
        Compute irradiance [W/m²] according to the counter
        """
        slope = (1000 - 300)/120
        sec = compteur %(7*60)
        if sec < 60:
            G = 300
        elif sec < 180:
            t = sec - 60 
            G = 300 + slope * t
        elif sec < 240:
            G = 1000
        elif sec < 360:
            t = sec - 240
            G = 1000 - slope * t
        elif sec < 420:
            G = 300
        return G
    
    ## PV info 
    
    V_oc_stc = 30
    FFI = 0.9
    FFU = 0.8
    
    nb_output = 2
    I_sc_stc = 5
    I_0 = I_sc_stc * (1-FFI)**(1/(1-FFU))
    C_AQ = (FFU - 1)/np.log(1-FFI)
    plot = dynamic_plot(V_oc_stc,I_sc_stc)
    time.sleep(10)
    compteur = 0
    
    ## Set up MX180TP + LD400P at initial conditions
    
    ## LD400P into Constant Current mode

    load_com.set_mode("C")
    G = irradiance(compteur)
        
    I_sc_init = I_sc_fct(G,I_sc_stc)
    V_oc_init = V_oc_fct(G,V_oc_stc)
    ## Switching ON the MX180TP
    I_supply = I_init + 0.1
    V_PV_init = V_oc_init * C_AQ * np.log(1 - (I_supply - I_sc_init)/I_0)
    
    
    supply_com.setup(V_PV_init,I_supply,nb_output)
    load_com.set_level("A",I_init)
    supply_com.output(nb_output,1)
    
    ## Switching ON the Load
    load_com.switch_load(1)
    time.sleep(20)
    
    V_meas_init, I_meas_init = supply_com.get_measurements(nb_output)
    P_meas_init = V_meas_init * I_meas_init
    
    I = I_init
    dI = 0.05
    while compteur < 2 * 7 * 60:
        G = irradiance(compteur)
        
        I_sc = I_sc_fct(G,I_sc_stc)
        V_oc = V_oc_fct(G,V_oc_stc)
        V_PV_array = np.linspace(0,V_oc,100)
        I_PV_array = (I_sc - I_0 * (np.exp(V_PV_array / (V_oc * C_AQ)) - 1)) - 0.1
        compteur += 1 
        time.sleep(0.5)
        V_meas_init, I_meas_init = supply_com.get_measurements(nb_output)
        P_meas_init = V_meas_init * I_meas_init
        
        ## Display it
        x,y,P = plot.add_point(V_meas_init,I_meas_init,V_PV_array,I_PV_array)
        
        if compteur == 1:
            if I + dI > I_sc:
                I -= dI
            else:
                I += dI 
    
        load_com.set_level("A",I) 
        I_supply = I + 0.1
        V_PV = V_oc * C_AQ * np.log(1 - (I_supply - I_sc)/I_0)
        
        
        supply_com.setup(V_PV,I_supply,nb_output)
        time.sleep(0.5)
        V_meas_new, I_meas_new = supply_com.get_measurements(nb_output)
        P_meas_new = V_meas_new * I_meas_new
        
        if P_meas_new > P_meas_init:
            if I_meas_new > I_meas_init:
                I += dI
            else:
                I -= dI
        else:
            if I_meas_new > I_meas_init:
                I -= dI
            else:
                I += dI
        
    ## Switch off the devices and disconnect    
    load_com.switch_load(0)
    supply_com.output(nb_output,0)
    load_com.close()
    supply_com.close()
    

## Configurate matplotlib
plt.ion()
## Connect with MX180TP

MX180TP_connect = MX180TP(None,None,"COM5")
MX180TP_connect.connect()

## Connect with LD400P

LD400P_connect = LD400P("192.168.0.49",9221,None) 
LD400P_connect.connect()

V_init = 10
I_init = 0.3
#MPPT_LD400P(I_init,LD400P_connect,MX180TP_connect,DynamicUpdate)

## Try with constant voltage mode

## PV info 

V_oc_stc = 30
FFI = 0.9
FFU = 0.8

nb_output = 2
I_sc_stc = 5
I_0 = I_sc_stc * (1-FFI)**(1/(1-FFU))
C_AQ = (FFU - 1)/np.log(1-FFI)
plot = DynamicUpdate(V_oc_stc,I_sc_stc)
time.sleep(10)
LD400P_connect.set_mode("V")
V_PV_init = V_init+ 0.2
I_supply = (I_sc_stc - I_0 * (np.exp(V_init / (V_oc_stc * C_AQ)) - 1))
MX180TP_connect.setup(V_PV_init,I_supply,nb_output)
LD400P_connect.set_level("A",V_init)
LD400P_connect.switch_load(1)
time.sleep(10)
MX180TP_connect.output(nb_output,1)

time.sleep(10)
## Switch off the devices and disconnect    
LD400P_connect.switch_load(0)
MX180TP_connect.output(nb_output,0)
MX180TP_connect.close()
LD400P_connect.close()