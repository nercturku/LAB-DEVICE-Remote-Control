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
import socket
import time
import numpy as np
import matplotlib.pyplot as plt
from dynamic_plot_LAB import DynamicUpdate 

class mode:
    """
    Defines the protocol of communication (either USB or LAN at the moment)
    Defines the communication settings 
    """
    def __init__(self,IP_ADDRESS,PORT_NUMBER,COM):
        if IP_ADDRESS == None:
            self.method = 'USB'
            self.address = None
            self.port = COM
        else:
            self.method = 'LAN'
            self.address = IP_ADDRESS
            self.port = PORT_NUMBER

class Communication:
    """ 
    Communication class for LAN or USB connection with AIMTTI Lab devices
    """
    def __init__(self,mode):
        
        """
        Parameters
        ----------
        mode : Dictionnary
            communication method : 'USB' or 'LAN'
            ADDRESS : None (USB) or IP_ADDRESS
            PORT : COM (USB) or TCP PORT
        """
        
        method,address,port = mode.method,mode.address,mode.port
        self.method = method
        if self.method == 'LAN':
            self.SUPPLY_IP = address
            self.SUPPLY_PORT = port
        elif self.method == 'USB':
            self.com = port
        else:
            print('Communication protocol not implemented yet')
    def connect(self):
        """ 
        Connect the computer with the device
        either serial communication or lan communcation
        """
        if self.method == 'LAN':
            TIMEOUT_SECONDS = 10
        
            ## Creating socket 
            supplySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # set up socket
            supplySocket.connect((self.SUPPLY_IP, self.SUPPLY_PORT)) # connect socket
            supplySocket.settimeout(TIMEOUT_SECONDS)
            self.source = supplySocket
        
        elif self.method == 'USB':
            self.source = serial.Serial(self.com,19200, 8, parity = 'N', timeout = 1)
    
    def close(self):
        """
        Disconnect the computer with the device
        either serial communication or lan communication
        """
        self.source.close()
            
    def sendCommand(self,msg):
        """ Converts the message into the message format for the mx180TP
        Adding a semi-colon separator '\r'
        Adding a new line '\n' to terminate the message
        Only send the message
        """
        com_msg = msg + "\r" + "\n"
        if self.method == 'LAN':
            self.source.sendall(com_msg.encode("UTF-8"))
        elif self.method == 'USB':
            self.source.write(com_msg.encode("UTF-8"))
    def sendAndReceiveCommand(self,msg):
        """ Converts the message into the message format for the mx180TP
        Adding a semi-colon separator '\r'
        Adding a new line '\n' to terminate the message
        Send the message and receive also the answer
        """
        com_msg = msg + "\r" + "\n"
        if self.method == 'LAN':
            BUFFER_SIZE = 256
            self.source.sendall(com_msg.encode("UTF-8"))
            return self.source.recv(BUFFER_SIZE).decode("UTF-8").rstrip()
        if self.method == 'USB':
            self.source.write(com_msg.encode("UTF-8"))
            return self.source.readline().decode("UTF-8")
        
            
class MX180TP:
    """
    Contains functions for remote control of MX180TP
    """
    def __init__(self,mode,Communication):
        """
        Parameters
        ----------
        mode : Dictionnanry
            Either USB or LAN communication
            gather IP_ADDRESS + PORT_Number
            or the number of the USB port
        Communication : class
            Enables the communication according to the chosen mode
        """
        
        ## Give the class communication and all the functions to MX180TP class
        self.Communication = Communication(mode)        

    
    def idn(self):
        """ Queries the Power Supply IDN. Prints the instrument identification as a string.
            \nArguments: COM port (str). Different string depending on the OS used.
            \nCommand to request IDN --> *IDN?
        """
        idn = self.Communication.sendAndReceiveCommand('*idn?')
        print('\nConnected...\nIDN: ', idn, '\n')
        
    
    
    def settings(self,nb_output):  # V
        """ Queries the Power Supply settings (Voltage, Current, Output). Prints the settings for OUTPUT1.
            \nArguments: COM port (str). Different string depending on the OS used.
            \nCommand to request Voltage --> V<N>?
            \nCurrent --> I<N>?
            \nOutput --> OP<N>?
            
        """
        
        voltage = self.Communication.sendAndReceiveCommand('V'+str(nb_output)+'?')
        print('\nVoltage ' + str(nb_output) + ' [V] =', voltage)
        current = self.Communication.sendAndReceiveCommand('I'+str(nb_output)+'?')
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
        self.Communication.sendCommand(V_command)
        self.Communication.sendCommand(I_command)
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
        self.Communication.sendCommand(command)
    
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
        output = self.Communication.sendAndReceiveCommand('OP' + str(nb_output) + '?')
        print('Status Output' + str(nb_output) + ' =', output)
        print('0 "OFF" 1 "ON"\n' )
    
    def get_measurements(self,nb_output):
        """
        Read the measurement (Current and Voltage) of the output nb_output
        Convert string answer into float
        """
        V_meas = self.Communication.sendAndReceiveCommand("V" + str(nb_output) + "O?")
        I_meas = self.Communication.sendAndReceiveCommand("I" + str(nb_output) + "O?")
        V_meas = float(V_meas[:5])
        I_meas = float(I_meas[:5])
        return V_meas, I_meas
class LD400P:
    """ 
    Contains functions for remote control of LD400P
    """
    def __init__(self,mode,Communication):
        """
        Connection with the LD400P through LAN communication
        normally port number should be 9221
        """
        self.Communication = Communication(mode)

    
    def set_mode(self,mode):
        """
        Choose the mode of the load 
        P : Constant Power
        C : Constant Current
        R : Constant Resistance
        G : Constant Conductance
        V : Constant Voltage
        """
        self.Communication.sendCommand("MODE "+ mode)
    
    def switch_load(self,state):
        """
        State : 0 (Off) or 1 (On) to switch on/off the load
        """
        self.Communication.sendCommand("INP " + str(state))
        
    def set600W(self,state):
        """
        
        Enable the 600W mode for the load
        Parameters
        ----------
        state : 0 or 1
            Off or On
        """
        self.Communication.sendCommand("600W " + str(state))
        
    def set_level(self,channel,value):
        self.Communication.sendCommand(channel + " " + str(value))
        
    def query_level(self,channel):
        query = self.Communication.sendAndReceiveCommand(channel + "?")
        return query
    
    def I_V_query(self):
        I = self.Communication.sendAndReceiveCommand("I?")
        V = self.Communication.sendAndReceiveCommand("V?")
        return I,V

    def set_limit(self,I_lim,V_lim):
        self.Communication.sendCommand("ILIM "+str(I_lim))
        self.Communication.sendCommand("VLIM "+str(V_lim))
    
    def query_limit(self):
        I_lim = self.Communication.sendAndReceiveCommand("ILIM?")
        V_lim = self.Communication.sendAndReceiveCommand("VLIM?")
        return I_lim,V_lim


if __name__ == '__main__':
    
    # Configurate matplotlib for dynamic plotting
    
    plt.ion()
    
    # Laptop assigned COM10 for the Power Supply
    
    COM = "COM5"
    mode_MX180TP = mode(None,None,COM)
    
    MX180TP_connect=MX180TP(mode_MX180TP,Communication)
    # connect device
    MX180TP_connect.Communication.connect()
    #Request IDN
    
    MX180TP_connect.idn()
    
    # Request voltage setup in the unit
    MX180TP_connect.settings(1)
    MX180TP_connect.output(1, 0)
    # Try Set up
    
    MX180TP_connect.setup(8.5,5,2)
    MX180TP_connect.output(2, 1)
    
    # Pause 20 seconds the time it is set
    
    time.sleep(80)
    MX180TP_connect.output(2, 0)
    
    # PV settings
    
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
        MX180TP_connect.setup(V_PV, I_PV, nb_output)
        x,y,P = plot.add_point(V_PV,I_PV)
        compteur += 1
    # Disconnect the COM port
    MX180TP_connect.Communication.close()
    
    # Set up the unit on/off
    #print('Executed succesfully!')
