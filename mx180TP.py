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

def connect(com): #V
    """ Opens the serial port.
        \nArguments: COM port (str). Different string depending on the OS used.
        \nReturns: A COM port object.
    """
    source = serial.Serial(com, 19200, 8, parity = 'N', timeout = 1)
    return source

def sendCommand(source, msg):
    
    """ Converts the message into the message format for the mx180TP
    Adding a semi-colon separator '\r'
    Adding a new line '\n' to terminate the message
    Only send the message
    """
    com_msg =  msg + + "\r" + "\n"
    source.write(com_msg.encode("UTF-8"))
    
def sendAndReceiveCommand(source,msg):
    
    """ Converts the message into the message format for the mx180TP
    Adding a semi-colon separator '\r'
    Adding a new line '\n' to terminate the message
    Send the message and receive also the answer
    """
    com_msg =  msg + + "\r" + "\n"
    source.write(com_msg.encode("UTF-8"))
    return source.readline().decode("UTF-8")

def idn(com):
    """ Queries the Power Supply IDN. Prints the instrument identification as a string.
        \nArguments: COM port (str). Different string depending on the OS used.
        \nCommand to request IDN --> *IDN?
    """
    power_source = connect(com)
    idn = sendAndReceiveCommand(power_source, '*idn?')
    print('\nConnected...\nIDN: ', idn, '\n')
    


def settings(com,nb_output):  # V
    """ Queries the Power Supply settings (Voltage, Current, Output). Prints the settings for OUTPUT1.
        \nArguments: COM port (str). Different string depending on the OS used.
        \nCommand to request Voltage --> V<N>?
        \nCurrent --> I<N>?
        \nOutput --> OP<N>?
        
    """
    power_source = connect(com)
    
    voltage = sendAndReceiveCommand(power_source, 'V'+str(nb_output)+'?')
    print('\nVoltage ' + str(nb_output) + ' [V] =', voltage)
    power_source.write(b'I1?\r\n')
    current = sendAndReceiveCommand(power_source, 'I'+str(nb_output)+'?')
    print('Current [A]=', current)
    power_source.write(b'OP1?\r\n')
    time.sleep(1)
    return voltage, current


def setup(com,Voltage,Current,nb_output):
    """ Sets up the Power Supply settings (Voltage, Current). Prints the new settings for OUTPUT1.
        \nArguments: COM port (str). Different string depending on the OS used.
        \nCommand to set up Voltage --> V<N> <NRF>
        \nCurrent --> I<N> <NRF>
    """
    power_source = connect(com)
    V_command = 'V' + str(nb_output) + ' ' + str(Voltage)
    I_command = 'I' + str(nb_output) + ' ' + str(Current)
    sendCommand(power_source, V_command)
    sendCommand(power_source, I_command)
    time.sleep(3)
    print("\nNew settings...\n")
    settings(com)
    


def output(com, nb_output, output):  # V
    """ Sets the OUTPUT associated to nb_output on/off.\n
        \nArguments:\n
        COM port (str). Different string depending on the OS used\n
        Output (0 for off, 1 for on)\n
        \nCommand to set up the output --> OP<N> <NRF>
        output = 0 or 1
        nb_ouput = 1, 2 or 3
    """
    power_source = connect(com)
    command = 'OP' + str(nb_output) + ' ' + str(output)
    sendCommand(power_source, command)

def status_output(com,nb_output):
    """
    read the status of the OUTPUT associated to nb_ourput on/off.\n
        \nArguments:\n
        COM port (str). Different string depending on the OS used\n
        Output (0 for off, 1 for on)\n
        \nCommand to set up the output --> OP<N> <NRF>
        output = 0 or 1
        nb_output = 1, 2 or 3
    """
    power_source = connect(com)
    output = sendAndReceiveCommand(power_source, 'OP' + str(nb_output) + '?')
    print('Status Output' + str(nb_output) + ' =', output)
    print('0 "OFF" 1 "ON"\n' )

# Laptop assigned COM10 for the Power Supply

COM = "/dev/ttyACM0"

# Request IDN
#idn(COM)

# Request voltage setup in the unit
#settings(COM)

# Set up
#setup(COM)

# Set up the unit on/off
#print('Executed succesfully!')
