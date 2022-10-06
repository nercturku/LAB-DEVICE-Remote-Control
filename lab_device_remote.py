# MX180TP Tripe Output Multi-Range DC Power Supply Controller
# Tested with Python 3.7.9 64-bit
# 15-MAR-22 Hugo Huerta
# SEP-22 Maximilien --> class reoganization
# OCT-22 Maximilien --> add LD400P class

# Few functions are available to control the MX180TP unit, for instance:
# Connection by using serial
# ID request
# Voltage and Current set up
# Output control ON/OFF
# Communication through LAN 

import socket
import time

class MX180TP:
    def __init__(self,IP_address,PORT_number):
        """
        Connection with the MX180TP through LAN communication
        normally port number should be 9221
        """
        self.SUPPLY_IP = IP_address
        self.SUPPLY_PORT = PORT_number
        
    def connectSocket(self):
        
        TIMEOUT_SECONDS = 10
        
        ## Creating socket 
        supplySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # set up socket
        supplySocket.connect((self.SUPPLY_IP, self.SUPPLY_PORT)) # connect socket
        supplySocket.settimeout(TIMEOUT_SECONDS)
        self.supply = supplySocket
        
    def sendCommand(self, msg):
        
        """ Converts the message into the message format for the mx180TP
        Adding a semi-colon separator '\r'
        Adding a new line '\n' to terminate the message
        Only send the message
        """
        com_msg =  msg + + "\r" + "\n"
        self.supply.sendall(com_msg.encode("UTF-8"))
        
    def sendAndReceiveCommand(self,msg):
        
        """ Converts the message into the message format for the mx180TP
        Adding a semi-colon separator '\r'
        Adding a new line '\n' to terminate the message
        Send the message and receive also the answer
        """
        BUFFER_SIZE = 256
        com_msg =  msg + + "\r" + "\n"
        self.supply.write(com_msg.encode("UTF-8"))
        return self.supply.recv(BUFFER_SIZE).decode("UTF-8").rstrip()
    
    def idn(self):
        """ Queries the Power Supply IDN. Prints the instrument identification as a string.
            \nArguments: COM port (str). Different string depending on the OS used.
            \nCommand to request IDN --> *IDN?
        """
        idn = MX180TP.sendAndReceiveCommand(self, '*idn?')
        print('\nConnected...\nIDN: ', idn, '\n')
        
    
    
    def settings(self,nb_output):  # V
        """ Queries the Power Supply settings (Voltage, Current, Output). Prints the settings for OUTPUT1.
            
            \nCommand to request Voltage --> V<N>?
            \nCurrent --> I<N>?
            \nOutput --> OP<N>?
            
        """
        
        voltage = MX180TP.sendAndReceiveCommand(self, 'V'+str(nb_output)+'?')
        print('\nVoltage ' + str(nb_output) + ' [V] =', voltage)
        current = MX180TP.sendAndReceiveCommand(self, 'I'+str(nb_output)+'?')
        print('Current [A]=', current)
        output = MX180TP.sendAndReceiveCommand(self,'OP' + str(nb_output) + '?')
        print('Output ' + str(nb_output) + ':', output  )
        time.sleep(1)
        return voltage, current
    
    
    def setup(self,Voltage,Current,nb_output):
        """ Sets up the Power Supply settings (Voltage, Current). Prints the new settings for OUTPUT1.
            \nArguments: COM port (str). Different string depending on the OS used.
            \nCommand to set up Voltage --> V<N> <NRF>
            \nCurrent --> I<N> <NRF>
        """
        V_command = 'V' + str(nb_output) + ' ' + str(Voltage)
        I_command = 'I' + str(nb_output) + ' ' + str(Current)
        MX180TP.sendCommand(self, V_command)
        MX180TP.sendCommand(self, I_command)
        time.sleep(3)
        print("\nNew settings...\n")
        MX180TP.settings(self,nb_output)
        
    
    
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
        MX180TP.sendCommand(self, command)
    
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
        output = MX180TP.sendAndReceiveCommand(self, 'OP' + str(nb_output) + '?')
        print('Status Output' + str(nb_output) + ' =', output)
        print('0 "OFF" 1 "ON"\n' )

class LD400P:
    def __init__(self,IP_address,PORT_number):
        """
        Connection with the LD400P through LAN communication
        normally port number should be 9221
        """
        self.SUPPLY_IP = IP_address
        self.SUPPLY_PORT = PORT_number
        
    def connectSocket(self):
        """
        Create + connect socket computer to lab device
        """
        TIMEOUT_SECONDS = 10
        
        supplySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # set up socket
        supplySocket.connect((self.SUPPLY_IP, self.SUPPLY_PORT)) # connect socket
        supplySocket.settimeout(TIMEOUT_SECONDS)
        self.supply = supplySocket
    
    def closeSocket(self):
        """
        disconnet socket computer to lab device
        """
        self.supply.close()
    
    def sendCommand(self, msg):
        
        """ Converts the message into the message format for the mx180TP
        Adding a semi-colon separator '\r'
        Adding a new line '\n' to terminate the message
        Only send the message
        """
        com_msg =  msg + + "\r" + "\n"
        self.supply.sendall(com_msg.encode("UTF-8"))
        
    def sendAndReceiveCommand(self,msg):
        
        """ Converts the message into the message format for the mx180TP
        Adding a semi-colon separator '\r'
        Adding a new line '\n' to terminate the message
        Send the message and receive also the answer
        """
        BUFFER_SIZE = 256
        com_msg =  msg + + "\r" + "\n"
        self.supply.write(com_msg.encode("UTF-8"))
        return self.supply.recv(BUFFER_SIZE).decode("UTF-8").rstrip()
    
    def set_mode(self,mode):
        """
        Choose the mode of the load 
        P : Constant Power
        C : Constant Current
        R = Constant Resistance
        G = Constant Conductance
        V = Constant Voltage
        """
        LD400P.sendCommand(self, "MODE "+ mode)
    
    def set600W(self,state):
        LD400P.sendCommand(self, "600W " + str(state))
        
    def set_level(self,channel,value):
        LD400P.sendCommand(self, channel + " " + str(value))
        
    def query_level(self,channel):
        query = LD400P.sendAndReceiveCommand(self, channel + "?")
        return query
    
    def I_V_query(self):
        I = LD400P.sendAndReceiveCommand(self, "I?")
        V = LD400P.sendAndReceiveCommand(self, "V?")
        return I,V

    def set_limit(self,I_lim,V_lim):
        LD400P.sendCommand(self,"ILIM "+str(I_lim))
        LD400P.sendCommand(self,"VLIM "+str(V_lim))
    
    def query_limit(self):
        I_lim = LD400P.sendAndReceiveCommand(self, "ILIM?")
        V_lim = LD400P.sendAndReceiveCommand(self, "VLIM?")
        return I_lim,V_lim
