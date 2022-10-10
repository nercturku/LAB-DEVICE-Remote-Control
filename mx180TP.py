# MX180TP Tripe Output Multi-Range DC Power Supply Controller
# Tested with Python 3.7.9 64-bit
# 15-MAR-22 Hugo Huerta
# SEP-22 Maximilien Marc --> adding PV functionnality

# Few functions are available to control the MX180TP unit, for instance:
# Connection by using serial
# ID request
# Voltage and Current set up
# Output control ON/OFF

import serial
import time
import numpy as np
import matplotlib.pyplot as plt
from dynamic_plot_LAB import DynamicUpdate 

class MX180TP_COM:
    def __init__(self,COM):
        self.com = COM

    def connect(self): #V
        """ Opens the serial port.
            \nArguments: COM port (str). Different string depending on the OS used.
            \nReturns: A COM port object.
        """
        self.source = serial.Serial(self.com, 19200, 8, parity = 'N', timeout = 1)
        
    
    def close(self):
        self.source.close()
    
    def sendCommand(self, msg):
        
        """ Converts the message into the message format for the mx180TP
        Adding a semi-colon separator '\r'
        Adding a new line '\n' to terminate the message
        Only send the message
        """
        com_msg =  msg + "\r" + "\n"
        self.source.write(com_msg.encode("UTF-8"))
        
    def sendAndReceiveCommand(self,msg):
        
        """ Converts the message into the message format for the mx180TP
        Adding a semi-colon separator '\r'
        Adding a new line '\n' to terminate the message
        Send the message and receive also the answer
        """
        com_msg =  msg + "\r" + "\n"
        self.source.write(com_msg.encode("UTF-8"))
        return self.source.readline().decode("UTF-8")
    
    def idn(self):
        """ Queries the Power Supply IDN. Prints the instrument identification as a string.
            \nArguments: COM port (str). Different string depending on the OS used.
            \nCommand to request IDN --> *IDN?
        """
        idn = self.sendAndReceiveCommand('*idn?')
        print('\nConnected...\nIDN: ', idn, '\n')
        
    
    
    def settings(self,nb_output):  # V
        """ Queries the Power Supply settings (Voltage, Current, Output). Prints the settings for OUTPUT1.
            \nArguments: COM port (str). Different string depending on the OS used.
            \nCommand to request Voltage --> V<N>?
            \nCurrent --> I<N>?
            \nOutput --> OP<N>?
            
        """
        
        voltage = self.sendAndReceiveCommand('V'+str(nb_output)+'?')
        print('\nVoltage ' + str(nb_output) + ' [V] =', voltage)
        current = self.sendAndReceiveCommand('I'+str(nb_output)+'?')
        print('Current ' + str(nb_output) + ' [A]=', current)
        time.sleep(0)
        return voltage, current
    
    
    def setup(self, Voltage,Current,nb_output):
        """ Sets up the Power Supply settings (Voltage, Current). Prints the new settings for OUTPUT1.
            \nArguments: COM port (str). Different string depending on the OS used.
            \nCommand to set up Voltage --> V<N> <NRF>
            \nCurrent --> I<N> <NRF>
        """
        V_command = 'V' + str(nb_output) + ' ' + str(Voltage)
        I_command = 'I' + str(nb_output) + ' ' + str(Current)
        self.sendCommand(V_command)
        self.sendCommand(I_command)
        time.sleep(0)
        print("\nNew settings...\n")
        voltage,current = self.settings(nb_output)
        return voltage,current
    
    
    def output(self, nb_output, output):  # V
        """ Sets the OUTPUT associated to nb_output on/off.\n
            \nArguments:\n
            COM port (str). Different string depending on the OS used\n
            Output (0 for off, 1 for on)\n
            \nCommand to set up the output --> OP<N> <NRF>
            output = 0 or 1
            nb_ouput = 1, 2 or 3
        """
        command = 'OP' + str(nb_output) + ' ' + str(output)
        self.sendCommand(command)
    
    def status_output(self,nb_output):
        """
        read the status of the OUTPUT associated to nb_ourput on/off.\n
            \nArguments:\n
            COM port (str). Different string depending on the OS used\n
            Output (0 for off, 1 for on)\n
            \nCommand to set up the output --> OP<N> <NRF>
            output = 0 or 1
            nb_output = 1, 2 or 3
        """
        output = self.sendAndReceiveCommand('OP' + str(nb_output) + '?')
        print('Status Output' + str(nb_output) + ' =', output)
        print('0 "OFF" 1 "ON"\n' )



if __name__ == '__main__':
    # Configurate matplotlib
    
    plt.ion()
    # Laptop assigned COM10 for the Power Supply
    
    COM = "COM4"
    
    MX180TP_COM_connect=MX180TP_COM(COM)
    # connect device
    MX180TP_COM_connect.connect()
    #Request IDN
    
    MX180TP_COM_connect.idn()
    
    # Request voltage setup in the unit
    MX180TP_COM_connect.settings(1)
    
    # Try Set up
    MX180TP_COM_connect.setup(8,5,2)
    
    V = np.linspace(0,30,100)
    V_0 = V[-1]
    FFI = 0.9
    FFU = 0.8
    
    compteur = 0
    nb_output = 2
    I_sc = 5
    I_0 = I_sc * (1-FFI)**(1/(1-FFU))
    C_AQ = (FFU - 1)/np.log(1-FFI)
    plot = DynamicUpdate(V_0,I_sc)
    ## Pause the time the GUI is setting up
    time.sleep(10)
    
    while compteur < len(V):
        time.sleep(1)
        V_PV = V[compteur]
        I_PV = I_sc - I_0 * (np.exp(V_PV / (V_0 * C_AQ)) - 1)
        MX180TP_COM_connect.setup(V_PV, I_PV, nb_output)
        x,y,P = plot.add_point(V_PV,I_PV)
        compteur += 1
    ## Disconnect the COM port
    MX180TP_COM_connect.close()
    
    # Set up the unit on/off
    #print('Executed succesfully!')
