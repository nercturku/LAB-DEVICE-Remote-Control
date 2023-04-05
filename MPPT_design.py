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
from PV_class import PV
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
    ## Create PV panel 
    
    PV_panel = PV(
        V_oc_stc = 30,
        I_sc_stc=5,
        FFI = 0.9,
        FFU = 0.8
        )

    plot = dynamic_plot(PV_panel.V_oc_stc, PV_panel.I_sc_stc, minute)
    time.sleep(10)
    count = 0
    
    ## Set up MX180TP + LD400P at initial conditions
    
    # LD400P into Constant Current mode
    nb_output = 2
    load_com.set_mode("C")
    load_com.set_level("A",I_init)
    PV_panel(count, mode, minute)
    
    ## Switching ON the MX180TP
    V_supply, I_supply = PV_panel.supply_settings(I_load = I_init)
    
    supply_com.setup(V_supply,I_supply,nb_output)
    supply_com.output(nb_output,1)
    
    ## Switching ON the Load
    load_com.switch_load(1)
    
    time.sleep(10)
    
    V_meas_old, I_meas_old, P_meas_old = supply_com.get_measurements(nb_output)
    
    I = I_init

    ## Initilize efficiency list
    eff = [P_meas_old/max(PV_panel.P_PV_array)]
    
    while count < minute * 60: 
        ## If dynamic mode --> change the irradiance and PV Curve
        PV_panel(count, mode, minute)
        V_supply, I_supply = PV_panel.supply_settings(I_load = I)
        supply_com.setup(V_supply,I_supply,nb_output)
        
        time.sleep(1)
        ## Get measurements
        V_meas_new, I_meas_new, P_meas_new = supply_com.get_measurements(nb_output)
        eff.append(P_meas_new/max(PV_panel.P_PV_array))
         
        plot.add_point(V_meas_new,
                        I_meas_new,
                        PV_panel.V_PV_array,
                        PV_panel.I_PV_array,
                        PV_panel.P_PV_array,
                        eff[-1],
                        PV_panel.G)

        ## Performs MPPT --> To be completed
        I = MPPT_function(I,
                  P_meas_old,
                  P_meas_new,
                  I_meas_old,
                  I_meas_new,
                  V_meas_old,
                  V_meas_new,
                  PV_panel.I_sc)

        ## Setting UP the Load and the Power Supply
        load_com.set_level("A",I) 
                 
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

def MPPT_function(I,
                  P_meas_old,
                  P_meas_new,
                  I_meas_old,
                  I_meas_new,
                  V_meas_old,
                  V_meas_new,
                  I_sc):
    """
    Performs MPPT by controlling the Load LD400P
    1) Fractional Short Circuit Current
    2) Perturb & Observ Algorithm
    3) Incremental Conductance Method

    Inputs:
        I: Current [A] that will command the behavior of the load
        P_meas_old: Power [W] measurement from the power supply (MX180TP, PV panel) at previous step
        P_meas_new: Power [W] measurement from the power supply (MX180TP, PV panel) at current step
        I_meas_old: Current [A] measurement from the power supply (MX180TP, PV panel) at previous step
        I_meas_new: Current [A] measurement from the power supply (MX180TP, PV panel) at current step
        V_meas_old: Voltage [V] measurement from the power supply (MX180TP, PV panel) at previous step
        V_meas_new: Voltage [V] measurement from the power supply (MX180TP, PV panel) at current step
        I_sc: Short Circuit Current [A] of the simulated PV Panel
    """
    
    return I 


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
new_fig.show()
input("press enter (keyboard) to close the figures")