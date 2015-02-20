#!/usr/bin/python
"""
  Basic class for communication to Parrot Bebop
  usage:
       ./bebop.py <task> [<metalog> [<F>]]
"""
import sys
import socket
import datetime
import struct
from navdata import *

# this will be in new separate repository as common library fo robotika Python-powered robots
from apyros.metalog import MetaLog, disableAsserts


# hits from https://github.com/ARDroneSDK3/ARSDKBuildUtils/issues/5

HOST = "192.168.42.1"
DISCOVERY_PORT = 44444

NAVDATA_PORT = 43210 # d2c_port
COMMAND_PORT = 54321 # c2d_port

class Bebop:
    def __init__( self, metalog=None ):
        if metalog is None:
            self._discovery()
            metalog = MetaLog()
        self.navdata = metalog.createLoggedSocket( "navdata", headerFormat="<BBBI" )
        self.navdata.bind( ('',NAVDATA_PORT) )
        self.command = metalog.createLoggedSocket( "cmd", headerFormat="<BBBI" )
        self.metalog = metalog
        self.buf = ""

    def _discovery( self ):
        "start communication with the robot"
        filename = "tmp.bin" # TODO combination outDir + date/time
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # TCP
        s.connect( (HOST, DISCOVERY_PORT) )
        s.send( '{"controller_type":"computer", "controller_name":"katarina", "d2c_port":"43210"}' )
        f = open( filename, "wb" )
        while True:
            data = s.recv(10240)
            if len(data) > 0:
                print len(data)
                f.write(data)
                f.flush()
                break
        f.close()
        s.close()

    def _update( self, cmd ):
        "internal send command and return navdata"
        while len(self.buf) == 0:
            data = self.navdata.recv(4094)
            self.buf += data
        if cmd is not None:
            self.command.sendto( cmd, (HOST, COMMAND_PORT) )
        self.command.separator( "\xFF" )
        data, self.buf = cutPacket( self.buf )
        return data

    def update( self, cmd ):
        "send command and return navdata"
        if cmd is None:
            data = self._update( None )
        else:
            data = self._update( packData(cmd) )
        while True:
            if ackRequired(data):
                data = self._update( createAckPacket(data) )
            elif pongRequired(data):
                data = self._update( createPongPacket(data) )
            elif videoAckRequired(data):
                data = self._update( createVideoAckPacket(data) )
            else:
                break

        return data


    # TODO rename these functions to xxxCmd so they can be prepared and not immediately called
    # maybe move it to separate file commands.py??
    def takeoff( self ):
        # ARCOMMANDS_ID_PROJECT_ARDRONE3 = 1,
        # ARCOMMANDS_ID_ARDRONE3_CLASS_PILOTING = 0,
        # ARCOMMANDS_ID_ARDRONE3_PILOTING_CMD_TAKEOFF = 1,
        self.update( cmd=struct.pack("BBH", 1, 0, 1) )
        
    def land( self ):
        # ARCOMMANDS_ID_PROJECT_ARDRONE3 = 1,
        # ARCOMMANDS_ID_ARDRONE3_CLASS_PILOTING = 0,
        # ARCOMMANDS_ID_ARDRONE3_PILOTING_CMD_LANDING = 3,
        self.update( cmd=struct.pack("BBH", 1, 0, 3) )

    def emergency( self ):
        # ARCOMMANDS_ID_PROJECT_ARDRONE3 = 1,
        # ARCOMMANDS_ID_ARDRONE3_CLASS_PILOTING = 0,
        # ARCOMMANDS_ID_ARDRONE3_PILOTING_CMD_EMERGENCY = 4,
        self.update( cmd=struct.pack("BBH", 1, 0, 4) )
    
    # TODO:
    # ARCOMMANDS_ID_ARDRONE3_PILOTING_CMD_FLATTRIM = 0,
    # ARCOMMANDS_ID_ARDRONE3_PILOTING_CMD_PCMD = 2,
   

    def videoEnable( self ):
        "enable video stream?"
        # ARCOMMANDS_ID_PROJECT_ARDRONE3 = 1,
        # ARCOMMANDS_ID_ARDRONE3_CLASS_MEDIASTREAMING = 21,
        # ARCOMMANDS_ID_ARDRONE3_MEDIASTREAMING_CMD_VIDEOENABLE = 0,        
        self.update( cmd=struct.pack("BBHB", 1, 21, 0, 1) )

    def moveCamera( self, tilt, pan ):
        "Tilt/Pan camera consign for the drone (in degrees)"
        # ARCOMMANDS_ID_PROJECT_ARDRONE3 = 1,
        # ARCOMMANDS_ID_ARDRONE3_CLASS_CAMERA = 1,
        # ARCOMMANDS_ID_ARDRONE3_CAMERA_CMD_ORIENTATION = 0,
        self.update( cmd=struct.pack("BBHbb", 1, 1, 0, tilt, pan) )

    def resetHome( self ):
        # ARCOMMANDS_ID_PROJECT_ARDRONE3 = 1
        # ARCOMMANDS_ID_ARDRONE3_CLASS_GPSSETTINGS = 23
        # ARCOMMANDS_ID_ARDRONE3_GPSSETTINGS_CMD_RESETHOME = 1
        self.update( cmd=struct.pack("BBH", 1, 23, 1) )


###############################################################################################

def testCamera( task, metalog ):
    robot = Bebop( metalog=metalog )
    for i in xrange(10):
        print -i,
        robot.update( cmd=None )
    robot.resetHome()
    robot.videoEnable()
    for i in xrange(100):
        print i,
        robot.update( cmd=None )
        robot.moveCamera( tilt=i, pan=i ) # up & right


def testEmergency( task, metalog ):
    "test of reported state change"
    robot = Bebop( metalog=metalog )
    robot.takeoff()
    robot.emergency()
    for i in xrange(10):
        print i,
        robot.update( cmd=None )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print __doc__
        sys.exit(2)
    metalog=None
    if len(sys.argv) > 2:
        metalog = MetaLog( filename=sys.argv[2] )
    if len(sys.argv) > 3 and sys.argv[3] == 'F':
        disableAsserts()
#    testCamera( sys.argv[1], metalog=metalog )
    testEmergency( sys.argv[1], metalog=metalog )

# vim: expandtab sw=4 ts=4 

