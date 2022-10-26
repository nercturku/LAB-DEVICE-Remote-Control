# -*- coding: utf-8 -*-
"""
Exercice Develop MPPT Algorithm with LD400P + MX180TP setup
Static Efficiency
Dynamic Efficiency
"""

## IMPORT
import time
import numpy as np
import matplotlib.pyplot as plt
from dynamic_plot_LAB import DynamicUpdate
from LAB_device_class import MX180TP, LD400P
from helloworld import COM_PORT_MX180TP,COM_PORT_LD400P


def MPPT_efficiency(I_init,load_com,supply_com,dynamic_plot,MPPT_function,mode,minute = 7):
    """
    Performs MPPT between a LD400P DC load and a MX180TP DC supply
    
    INPUTS : 
    load_com is the objected connected with LD400P
    supply_com is the object connected with MX180TP
    
    MPPT_function is the MPPT function to command the LD400P
    mode : string 'static' or 'dynamic'
    minute : number of minutes
    OUTPUTS:
    eff : efficiency P_meas_MPPT/P_MPP_PV
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
    
    def irradiance(count,mode,minute):
        """
        Compute irradiance [W/m²] according to the counter and the simulation mode
        """
        if mode == 'dynamic':
            slope = (1000 - 300)/(120 * minute / 7)
            sec = count %(minute*60)
            if sec < 60 * minute/7:
                G = 300
            elif sec < 60 * minute * 3 / 7:
                t = sec - 60 * minute /7 
                G = 300 + slope * t
            elif sec < 60 * minute * 4/7:
                G = 1000
            elif sec < 60 * minute * 6/7:
                t = sec - 60 * minute * 4/7
                G = 1000 - slope * t
            elif sec < 60 * minute:
                G = 300
        elif mode == 'static':
            G = 1000
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
    count = 0
    
    ## Set up MX180TP + LD400P at initial conditions
    
    ## LD400P into Constant Current mode

    load_com.set_mode("C")
    G = irradiance(count,mode,minute)
        
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
    I_step = 0.05

    ## Initilize eff list
    eff = [] 
    
    while count < minute * 60: 
        
        G = irradiance(count,mode,minute)
        
        I_sc = I_sc_fct(G,I_sc_stc)
        V_oc = V_oc_fct(G,V_oc_stc)
        V_PV_array = np.linspace(0,V_oc,100)
        I_PV_array = (I_sc - I_0 * (np.exp(V_PV_array / (V_oc * C_AQ)) - 1)) - 0.1
        count += 1 
        
        ## Display it --> on figure
        x,y,P,P_PV_array = plot.add_point(V_meas_init,I_meas_init,V_PV_array,I_PV_array)
        eff.append(P_meas_init/max(P_PV_array))

        ## Setting UP the Load and the Power Supply

        load_com.set_level("A",I) 
        I_supply = I + 0.1 # Add 0.1 to have the settings current of the power supply higher than the one of the load
        V_PV = V_oc * C_AQ * np.log(1 - (I_supply - I_sc)/I_0) # PV voltage accoridng to current
        
        
        supply_com.setup(V_PV,I_supply,nb_output)
        time.sleep(1)

        ## Get measurements
        V_meas_new, I_meas_new = supply_com.get_measurements(nb_output)
        P_meas_new = V_meas_new * I_meas_new
        
        ## Performs MPPT --> To be completed

        output = MPPT_function()

        ## Store Old Measurement
        P_meas_init,I_meas_init,V_meas_init = P_meas_new,I_meas_new,V_meas_new

        
        
        
    ## Switch off the devices and disconnect    
    load_com.switch_load(0)
    supply_com.output(nb_output,0)
    load_com.close()
    supply_com.close()
    return eff

def MPPT_function():
    """
    Performs MPPT by controlling the LD400P
    1) Perturb & Observ Algorithm
    2) Incremental Conductance Method --> To be tested
    """  
    return None


## Configurate matplotlib for dynamic plots
plt.ion()

## Connect with MX180TP

MX180TP_object = MX180TP(None,None,COM_PORT_MX180TP)
MX180TP_object.connect()

## Connect with LD400P

LD400P_object = LD400P(None,None,COM_PORT_LD400P) 
LD400P_object.connect()


## initial current for the PowerSupply
I_init = 0.3

## Simulation mode
mode = 'static' # either static or dynamic

eff = MPPT_efficiency(I_init,LD400P_object,MX180TP_object,DynamicUpdate,MPPT_function,mode,minute = 1) # MPPT Efficiency

new_fig, ax = plt.subplots()
ax.plot([i for i in range(len(eff))],eff)
ax.set_ylabel('MPPT Efficiency')
ax.set_xlabel('Time (s)')
ax.set_ylim([0,1])
plt.show()