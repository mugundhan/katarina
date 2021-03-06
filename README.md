Katarina
=======

Parrot drone Bebop

* autonomous drone controlled via Python

For detail info see
http://robotika.cz/robots/katarina/

![Katarina Bebop Drone](http://robotika.cz/robots/katarina/katarina.jpg)

# Notes/Howto

First of all note, that this experimental project is *work in progress* and it
is your responsibility if you decide to use it without understanding the risks.
Inspiration and message codes are taken from official Parrot SDK:
https://github.com/ARDroneSDK3

The goal for Katarina repository is tha same as for Heidi
(https://github.com/robotika/heidi) ARDrone2 --- autonomous flying programmed
in Python. The code is developed and tested on laptop running Win7 and Python
2.7 but it should be easy to port it to other OS. Image processing uses OpenCV2
and NumPy libraries.

Code example:
```
drone = Bebop()
drone.takeoff()
drone.flyToAltitude(2.0)
drone.takePicture()
drone.land()
```

Surely the code becomes more complicated if you want to integrate video
processing or complex navigation. On the other hand it is relatively short so
you may read details "what is going on" ;-). Every run it logged and you should
be able to immediately replay it. See "bebop.py" file for example(s).

Warning! Autonomous flights sometimes turn bad ... and you need to stop the
drone ASAP. For my simple experiments landing is so far good choice what to do,
so as soon as I hit any key, the ManualControlException is raised and
alternative code is performed (typically combination of land() and
emergency() due to unlucky implementation of state machine on ARDrone3). This
means that the code above should be wrapped into try .. except
ManualControlException block.

The code evolved into several files:

* bebop.py --- this is the main file you need to import. The class Bebop
connects to the drone, contains up-to-date status variables and methods for
basic flight operations. There are several ""test"" demos, which follow the
experiments (and it will be probably moved to separate file).

* commands.py --- here you find list of some basic ARDrone3 commands
converting name into few bytes packet.

* navdata.py --- parsing of (not only) navigation data. The name was taken from
ARDrone2. You can use this script also for detail verbose dump of recorded
"navdata" log.

* video.py --- handing of parts of H264 video frames. Also serves as utility
  for video conversion and extraction of individual frames.

* play.py --- play video using OpenCV2 (uses video.py as conversion routine, if
  necessary).

* capdet.py --- two color Parrot cap detection experiment (reference colors are
  stored in cap-colors.txt).

* apyros folder --- logging tools, shared among several Python driven robots.
  This folder is planned be moved into separate repository.

* demo.py --- integration of image processing with flight control (work in
  progress)


# FAQ

Q: I recently succeed to launch demo.py but I've a question about the 
parameter "task" in some of your scripts, is there any list of task that 
i should use to launch these scripts ? Are this just a name given to the 
instance of the demo ?

A: The "task" parameter is dummy at the moment. It should be named rather
"comment", because this is the way how I mainly use it (it is automatically
stored in metalog file), i.e. testWithTakeoffInWindyCondition. The plan is
to use it for "task selection" in the future ...


