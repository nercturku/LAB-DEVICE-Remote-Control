# MX180TP Tripe Output Multi-Range DC Power Supply Controller
# Tested with Python 3.7.9 64-bit
# 15-MAR-22 Hugo Huerta

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


def idn(com):  # V
    """ Queries the Power Supply IDN. Prints the instrument identification as a string.
        \nArguments: COM port (str). Different string depending on the OS used.
        \nCommand to request IDN --> *IDN?
    """
    power_source = connect(com)
    power_source.write(b'*idn?\r\n')
    id = power_source.readline().decode("utf-8")
    print('\nConnected...\nIDN: ', id, '\n')
    return()


def settings(com):  # V
    """ Queries the Power Supply settings (Voltage, Current, Output). Prints the settings for OUTPUT1.
        \nArguments: COM port (str). Different string depending on the OS used.
        \nCommand to request Voltage --> V<N>?
        \nCurrent --> I<N>?
        \nOutput --> OP<N>?
    """
    power_source = connect(com)
    power_source.write(b'V1?\r\n')
    voltage = power_source.readline().decode("utf-8")
    print('\nVoltage [V] =', voltage)
    power_source.write(b'I1?\r\n')
    current = power_source.readline().decode("utf-8")
    print('Current [A]=', current)
    power_source.write(b'OP1?\r\n')
    output = power_source.readline().decode("utf-8")
    print('Status Output1 =', output)
    print('0 "OFF" 1 "ON"\n' )
    time.sleep(1)
    return()


def setup(com):
    """ Sets up the Power Supply settings (Voltage, Current). Prints the new settings for OUTPUT1.
        \nArguments: COM port (str). Different string depending on the OS used.
        \nCommand to set up Voltage --> V<N> <NRF>
        \nCurrent --> I<N> <NRF>
    """
    power_source = connect(com)
    power_source.write(b'V1 3.3\r\n')
    power_source.write(b'I1 0.2\r\n')
    time.sleep(3)
    print("\nNew settings...\n")
    settings(com)
    return()


def output(com, output):  # V
    """ Sets the OUTPUT1 on/off.\n
        \nArguments:\n
        COM port (str). Different string depending on the OS used\n
        Output (0 for off, 1 for on)\n
        \nCommand to set up the output --> OP<N> <NRF>
    """
    power_source = connect(com)
    command = 'OP1 ' + str(output) + '\r\n'
    S = str.encode(command)
    power_source.write(S)
    status = power_source.readline().decode("utf-8")
    print('Status=', status)
    return()

# Laptop assigned COM10 for the Power Supply

COM = "/dev/ttyACM0"

# Request IDN
#idn(COM)

# Request voltage setup in the unit
#settings(COM)

# Set up
#setup(COM)

# Set up the unit on/off
#rint('Executed succesfully!')
