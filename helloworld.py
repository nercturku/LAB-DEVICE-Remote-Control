from LAB_device_class import MX180TP,LD400P
import time


if __name__ == '__main__':
    ## Connect with MX180TP
    
    MX180TP_object = MX180TP() ## get the object
    MX180TP_object.connect()
        
    
    ## Connect with LD400P
    
    LD400P_object = LD400P() ## get the object
    LD400P_object.connect()
    
    ## Ask for identification
    
    MX180TP_object.idn()
    LD400P_object.idn()
    
    
    ## 3. Switching on/off the devices --> To be completed
    # Example
    I_load = 2 # [A] settings for the load 
    
    V_supply = 20 # [V] voltage setting for supply
    I_supply = 4 # [A] current setting for supply
    
    MX180TP_object.setup(V_supply,I_supply,2) # Setup Voltage, current on output number 2
    LD400P_object.set_mode("C") # Load in Current Mode
    LD400P_object.set_level("A",I_load) # Set load's channel A to I_load
    
    LD400P_object.switch_load(1) # Switch on the load
    MX180TP_object.output(2,1) # Switch on the supply
    
    time.sleep(5)
    V_meas,I_meas = MX180TP_object.get_measurements(2) # Get measurement from output 2
    print("V_meas = {0} V".format(V_meas))
    print("I_meas = {0} A".format(I_meas))
    time.sleep(5)
    
    LD400P_object.switch_load(0) # Switch off the load
    MX180TP_object.output(2,0) # Switch off the supply
    
    ## Disconnect Devices
    
    MX180TP_object.close()
    LD400P_object.close()