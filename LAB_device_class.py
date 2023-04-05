# Tested with Python 3.7.9 64-bit
# 15-MAR-22 Hugo Huerta
# SEP-22 Maximilien Marc --> ADD Class for communication
# 4 class mode, Communication, MX180TP, LD400P
# mode --> either LAN or USB 
# Communication --> connect, disconnect, send and revices command with devices
# MX180TP --> functions related with power supply
# LD400P --> functions related with DC Load

import serial # USB Com
import socket # Lan Com
import time
import serial.tools.list_ports # List ports connected to computer
import os
from sys import exit

class mode:
    """
    Defines the protocol of communication (either USB or LAN at the moment)
    Defines the communication settings 
    """
    def __init__(self):
        PID = self.PID
        name = self.name
        try:
            USB = False
            ## Try to find the USB COM ports associated with PID
            for serial_object in serial.tools.list_ports.comports():
                if serial_object.pid == PID:
                    COM = serial_object.device
                    self.method = 'USB'
                    self.com = COM
                    USB = True
            if not USB:
                LAN = False
                ## Supply port of aim-TTI
                self.SUPPLY_PORT = 9221
                ## Try to connect with IP address associated with the PID
                devices = []
                for device in os.popen('arp -a'):
                    devices.append(device)
                
                
                List_IP_address = []
                for device in devices:
                    try:
                        
                        int(device[2])
                        IP_ADDRESS = device[2:17]
                        
                        loop = True
                        while loop:
                            if IP_ADDRESS[-1] == " ":
                                IP_ADDRESS = IP_ADDRESS[:-1]
                            else:
                                loop = False
                        List_IP_address.append(IP_ADDRESS)
                        
                        ## Try to connect with IP address on supply port
                        try:
                            TIMEOUT_SECONDS = 0.01
                            ## Creating socket  to connect with the supply port
                            supplySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # set up socket
                            supplySocket.connect((IP_ADDRESS, self.SUPPLY_PORT)) # connect socket
                            supplySocket.settimeout(TIMEOUT_SECONDS)
                            ## Ask for identification for the item
                            idn_str = '*idn?' + '\r' + '\n'
                            supplySocket.sendall(idn_str.encode("UTF-8"))
                            idn_answer = supplySocket.recv(256).decode("UTF-8").rstrip()
                
                            if name in idn_answer:
                                ## if name in identification --> good items
                                ## store IP + connection method
                                self.SUPPLY_IP = IP_ADDRESS
                                self.method = 'LAN'
                                LAN = True
                                supplySocket.close()
                            else:
                                supplySocket.close()
                        except:
                            pass
                            
                        
                    except:
                        pass
                if USB == False and LAN == False:
                    raise Exception(name + ' No connection')
                        
        except:
            exit(name + ' neither USB nor LAN connected')
        

class Communication(mode):
    """ 
    Communication class for LAN or USB connection with AIMTTI Lab devices
    """
    def __init__(self):
        
        """
        Parameters
        ----------
        mode : Dictionnary
            communication method : 'USB' or 'LAN'
            ADDRESS : None (USB) or IP_ADDRESS
            PORT : COM (USB) or TCP PORT
        """
        
        mode.__init__(self)

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
        
            
class MX180TP(Communication):
    """
    Contains functions for remote control of MX180TP
    """
    def __init__(self):
        """
        Parameters
        ----------
        """
        
        ## Give the class communication and all the functions to MX180TP class
        self.PID = 1210
        self.name = "MX180TP"
        Communication.__init__(self)        

    
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
    
    def get_measurements(self,nb_output):
        """
        Read the measurement (Current and Voltage) of the output nb_output
        Convert string answer into float
        """
        V_meas = self.sendAndReceiveCommand("V" + str(nb_output) + "O?")
        I_meas = self.sendAndReceiveCommand("I" + str(nb_output) + "O?")
        V_meas = float(V_meas[:5])
        I_meas = float(I_meas[:5])
        P_meas = V_meas * I_meas
        return V_meas, I_meas, P_meas

class LD400P(Communication):
    """ 
    Contains functions for remote control of LD400P
    """
    def __init__(self):
        """
        Connection with the LD400P through LAN communication
        normally port number should be 9221
        """
        self.PID = 1200
        self.name = 'LD400P'
        Communication.__init__(self)

    def idn(self):
        """ Queries the Load IDN. Prints the instrument identification as a string.
            \nArguments: COM port (str). Different string depending on the OS used.
            \nCommand to request IDN --> *IDN?
        """
        idn = self.sendAndReceiveCommand('*idn?')
        print('\nConnected...\nIDN: ', idn, '\n')
    
    def set_mode(self,mode):
        """
        Choose the mode of the load 
        P : Constant Power
        C : Constant Current
        R : Constant Resistance
        G : Constant Conductance
        V : Constant Voltage
        """
        self.sendCommand("MODE "+ mode)
    
    def switch_load(self,state):
        """
        State : 0 (Off) or 1 (On) to switch on/off the load
        """
        self.sendCommand("INP " + str(state))
        
    def set600W(self,state):
        """
        
        Enable the 600W mode for the load
        Parameters
        ----------
        state : 0 or 1
            Off or On
        """
        self.sendCommand("600W " + str(state))
        
    def set_level(self,channel,value):
        self.sendCommand(channel + " " + str(value))
        
    def query_level(self,channel):
        query = self.sendAndReceiveCommand(channel + "?")
        return query
    
    def I_V_query(self):
        I = self.sendAndReceiveCommand("I?")
        V = self.sendAndReceiveCommand("V?")
        return I,V

    def set_limit(self,I_lim,V_lim):
        self.sendCommand("ILIM "+str(I_lim))
        self.sendCommand("VLIM "+str(V_lim))
    
    def query_limit(self):
        I_lim = self.sendAndReceiveCommand("ILIM?")
        V_lim = self.sendAndReceiveCommand("VLIM?")
        return I_lim,V_lim
    
    def level_select(self, channel: str):
        """
        Change the channel of the LD400P
        - channel: str,
            'A': A
            'B': B
            'T': Transient
            'V': Ext Voltage
            'E': Ext TTL
        """
        self.sendCommand(f"LVLSEL {channel}")
        chan = self.sendAndReceiveCommand("LVLSEL?")
        return chan 

if __name__ == '__main__':
    MX180TP_object = MX180TP()
    MX180TP_object.connect()
    MX180TP_object.idn()
    print(MX180TP_object.method)
    MX180TP_object.close()
    LD400P_object = LD400P()
    LD400P_object.connect()
    LD400P_object.idn()
    print(LD400P_object.method)
    LD400P_object.close()