#!/usr/bin/python
"""
  Parsing of incomming messages from Parrot Bebop
  usage:
       ./navdata.py <logged file>
"""
import sys
import struct

def printHex( data ):
    print " ".join(["%02X" % ord(x) for x in data])

def parseData( data ):
    assert data[0] == chr(0x2), ord(data[0])    
    assert ord(data[1]) in [0x7F, 0x0], ord(data[1])
    counter = ord(data[2])
    size = ord(data[3])
    assert size in [15, 19, 23, 35], size
    if ord(data[1]) == 0x7F:
        commandProject, commandClass, commandId = struct.unpack("BBH",  data[7:7+4])
        assert commandProject == 1, commandProject
        if (commandClass, commandId) == (4,4):
            lat, lon, alt = struct.unpack("ddd", data[11:11+3*8])
            print "Position", lat, lon, alt
        if (commandClass, commandId) == (4,5):
            speedX, speedY, speedZ = struct.unpack("fff", data[11:11+3*4])
            print "Speed", speedX, speedY, speedZ
        if (commandClass, commandId) == (4,6):
            roll, pitch, yaw = struct.unpack("fff", data[11:11+3*4])
            print "Angle", roll, pitch, yaw
        if (commandClass, commandId) == (4,8):
            altitude = struct.unpack("d", data[11:11+8])[0]
            print "Altitude", altitude
    data = data[size:]
    return data

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print __doc__
        sys.exit(2)
    data = open(sys.argv[1], "rb").read()
    while data:
        data = parseData( data )

# vim: expandtab sw=4 ts=4 
