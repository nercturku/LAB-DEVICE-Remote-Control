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
    plot = dynamic_plot(V_oc_stc,I_sc_stc, minute)
    time.sleep(10)
    count = 0
    
    ## Set up MX180TP + LD400P at initial conditions
    
    ## LD400P into Constant Current mode

    load_com.set_mode("C")
    G = irradiance(count,mode,minute)

    I_sc_init = I_sc_fct(G,I_sc_stc)
    V_oc_init = V_oc_fct(G,V_oc_stc)
    
    V_PV_array = np.linspace(0,V_oc_init,1000)
    I_PV_array = (I_sc_init - I_0 * (np.exp(V_PV_array / (V_oc_init * C_AQ)) - 1)) - 0.1
    ## Display it --> on figure
    P_PV_array = []
    for k in range(len(V_PV_array)):
        P_PV_array.append(V_PV_array[k] * I_PV_array[k])
    
    ## Switching ON the MX180TP
    I_supply = I_init + 0.1
    V_PV_init = V_oc_init * C_AQ * np.log(1 - (I_supply - I_sc_init)/I_0)
    
    
    supply_com.setup(V_PV_init,I_supply,nb_output)
    load_com.set_level("A",I_init)
    supply_com.output(nb_output,1)
    
    ## Switching ON the Load
    load_com.switch_load(1)
    time.sleep(10)
    
    V_meas_init, I_meas_init = supply_com.get_measurements(nb_output)
    P_meas_init = V_meas_init * I_meas_init
    
    I = I_init

    ## Initilize eff list
    eff = [P_meas_init/max(P_PV_array)]
    
    while count < minute * 60: 
        
        ## If dynamic mode --> change the irradiance and PV Curve
        G = irradiance(count,mode,minute) 
        I_sc = I_sc_fct(G,I_sc_stc)
        V_oc = V_oc_fct(G,V_oc_stc)
        V_PV_array = np.linspace(0,V_oc,1000)
        I_PV_array = (I_sc - I_0 * (np.exp(V_PV_array / (V_oc * C_AQ)) - 1)) - 0.1
        V_PV = V_oc * C_AQ * np.log(1 - (I_supply - I_sc)/I_0) # PV voltage accoridng to current
        supply_com.setup(V_PV,I_supply,nb_output)
        
        
        time.sleep(1)
        ## Get measurements
        V_meas_new, I_meas_new = supply_com.get_measurements(nb_output)
        P_meas_new = V_meas_new * I_meas_new
        eff.append(P_meas_new/max(P_PV_array))
        
        ## Display measurements
        P_PV_array = []
        for k in range(len(V_PV_array)):
            P_PV_array.append(V_PV_array[k] * I_PV_array[k])
         
        x,y,P,P_PV_array = plot.add_point(V_meas_new,
                                          I_meas_new,
                                          V_PV_array,
                                          I_PV_array,
                                          P_PV_array,
                                          eff[-1],
                                          G)


        
        ## Performs MPPT --> To be completed

        MPPT_function()

        ## Setting UP the Load and the Power Supply

        load_com.set_level("A",I) 
         
        I_supply = I + 0.1 # Add 0.1 to have the settings current of the power supply higher than the one of the load
        
        
        ## Store Old Measurement
        
        P_meas_old, V_meas_old, I_meas_old = P_meas_new, V_meas_new, I_meas_new
        
        count += 1
        
        
        
    ## Switch off the devices and disconnect    
    load_com.switch_load(0)
    supply_com.output(nb_output,0)
    load_com.close()
    supply_com.close()
    average_eff = sum(eff)/len(eff)
    return eff, average_eff

def MPPT_function():
    """
    Performs MPPT by controlling the LD400P
    1) Fractional Short Circuit Voltage
    2) Perturb & Observ Algorithm
    3) Incremental Conductance Method
    """
    pass


## Configurate matplotlib for dynamic plots
plt.ion()

## Connect with MX180TP

MX180TP_object = MX180TP()
MX180TP_object.connect()

## Connect with LD400P

LD400P_object = LD400P() 
LD400P_object.connect()


## initial current for the PowerSupply
I_init = 0.5

## Simulation mode
mode = 'static' # either static or dynamic
minute = 1
eff, average_eff = MPPT_efficiency(I_init,LD400P_object,MX180TP_object,DynamicUpdate,MPPT_function,mode,minute) # MPPT Efficiency

new_fig, ax = plt.subplots()
ax.plot([i for i in range(len(eff))],eff)
ax.set_ylabel('MPPT Efficiency')
ax.set_xlabel('Time (s)')
ax.set_ylim([0,1.1])
plt.show()