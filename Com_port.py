# -*- coding: utf-8 -*-
"""
Created on Tue Nov 28 22:23:04 2017

@author: ARPES
"""

def get_pressure (com_name):

    import serial.tools.list_ports
    import io
    
    """ This part maps all available COM ports """
#    list_com=serial.tools.list_ports.comports()
#    for i in list_com:
#        print (i.device,"  ", i.description)
    
    
    """ Open COM-port and send/read the command"""
    ser = serial.Serial(com_name,                   
                         baudrate=9600,
                         bytesize=serial.EIGHTBITS,
                         parity=serial.PARITY_NONE,
                         stopbits=serial.STOPBITS_ONE,
                         timeout=0.1)
#    print ("Listening port: ", ser.name)
    ser_io = io.TextIOWrapper(io.BufferedRWPair(ser, ser, 1),  
                               newline = '\r',
                               line_buffering = True)
    
    """Write a command(s) to pressure controller and read the reply """
    ser_io.write("#000F\r")
    read_str = ser_io.readline()[1:]
    #ser_io.write("#0002I2\r")
    #read_str1 = ser_io.readline()
    #read_str1=float(read_str1[1:])
    #
    #ser_io.write("#0002I1\r")
    #read_str2 = ser_io.readline()
    #read_str1.append(float(read_str2[1:]))
    
    ser.close()
    return read_str
#print (read_str)
