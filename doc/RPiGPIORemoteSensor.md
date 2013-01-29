Use the Raspberry Pi GPIO Remote Sensor Client
==============================================
15.01.2013 Stefan Wendler
sw@kaltpost.de


Introduction
------------

This document describes how to use the wrapper for the build in GPIOs of the Raspberry Pi.i The wrapper alows you to configure and access the GPIOs of the Pi from within scratch, using the Scratch remote sensor protocol [as described here] (http://wiki.scratch.mit.edu/wiki/Remote_Sensors_Protocol). Setting or getting the values of a GPIO pin from Scratch could be done by simply defining certain global varaiables.  

_Note:_ Only limited digital IO is possible through this API (no ADC, no PWM).

To see, how to install the API see the [README] (../README.md) that is included.


Start the Pi Sensor Daemon
--------------------------

When installing the Python API as described [here] (../README.md), also a start-script called ``srspid`` is installed. Calling this script without any parameters will start a sensor client for the PI GPIOs trying to connect to a Scratch sensor server instance on localhost:

	srspid start

_Note:_ it is perfectly fine to run the Scratch server on a different machine. Just pass the IP of that machine to the daemon script like so: ``srspid start 192.168.1.20``.

At the moment the daemon is started, a log-file is created in ``/var/log/srsd-pi.log``. If you like, you could monitor the daemons state e.g. by using tail:

	tail -f /var/log/srsd-pi.log

_Note:_ as long as no sensor server is running within Scratch, you will see the daemon retrying to connect.
 

If you do not need the daemon any more you could stop it with the following command:

	srspid stop 


Connect Scratch to the Daemon
------------------------------

Start Scratch and activate the remote sensor protocol by using the right click menu on one of the sensor blocks. For a more detailed description of how to [enable/use remote sensors] (http://wiki.scratch.mit.edu/wiki/Remote_Sensor_Connections) see the Scratch Wiki.

At the moment you active the remote sensor protocol, the ``srspid`` imidiatly connects to that server instance. 

_Hint:_ if you like to run the client and the server on the same machine, instaed of starting ``srspid`` and ``scratch`` individually, you could use the following shortcut:

	scratch-pirs

This will start ``srspid``, then Scratch. At the moment you quit Scratch, the ``srspid`` is stopped too.


How it Works 
------------

**Set the Direction of a Port**

The remote sonsor started by ``srspid`` allows you to control the build in GPIOs of a Raspberry Pi through global varaibales in Scratch.  The following variables are known by ``srspid`` for setting the direction of an GPIO (output or input):

* DIO4, DIO17, DIO18, DIO21, DIO22, DIO23, DIO24, DIO25

Assigning 0 to a DIOx variable configures the port as an output. By assigning 1 the port will be configured to be in input with internal pull-down enabled. 

E.g. to make IO port 25 an output, go to to "variables" in Scratch and define a new global varaiable named "DIO25". Now place a "set variable" block in the working area, select "DIO25" and assigne 0 to it. 

E.g. to make IO port 24 an input, go to to "variables" in Scratch and define a new global varaiable named "DIO24". Now place a "set variable" block in the working area, select "DIO24" and assigne 1 to it. 

_Note:_ by default, all ports are configured as inputs, thus, you do not need to assigne 0 to them.


**Set(Get the Value of a Port**

To set/get the current value (high/low) of an port, use the following variables:

* IO4, IO17, IO18, IO21, IO22, IO23, IO24, IO25

If a port is configured as an output, assigning 1 will set it to high, and asisigning 0 will set it to low. 

If a port is configured as an input, the remote sensor will constantly monitor this port for state change. Every time a state change is detected, a sensor-update message is sent to Scratch. E.g. if port 24 is configured as input, and its state changes from low to high this is reported imidiately to Scratch.

Additionally the message "input-changed" is broadcasted to the server is a state change for at least one of the input ports was detected. 

Thus, to read the value of a port from Scratch, insert the sensor value block and select the coresponding port varaible (e.g. IO24).

_Hint:_ to check in scratch for changed input ports, listen to the message "input-changed", and at the moment the message was received, check if the port of interest changed. This is much more efficent then polling a port variable directely in a loop.


**Sensor Client Hear-Beat**

Additonally, this remote sensor broadcasts a "heartbeat-pi" message every 5sec. to show it is still alive. This is mainly used internally to get aware of connection loss and to initiate a reconnect. 
