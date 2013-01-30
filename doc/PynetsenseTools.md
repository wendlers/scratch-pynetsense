Scratch Networking Sensor Client Library Tools
===============================================
30.01.2013 Stefan Wendler
sw@kaltpost.de


Introduction
------------

The Pynetsense API comes with a bunch of tools that might come in handy when you are going to develop your own sensor clients. This document briefly describes which tools are available and how to use them. 

To see, how to install the API see the [README] (../README.md) that is included.


Dummy Sensor Server
-------------------

For basic client testing, a simple Scratch remote sensor dummy server implementation (``srsds``) is provided. This dummy server accepts one sensor client at a time to connect. All messages received from the client are displayed on the the dummy servers console. Every line that was typed into the servers command line is send to the client.

To start the dummy server use the following command:

	srsds

This will open up a console (including read-line support). To get a short help on the usage of the ``srsds``, type in ``/h``. If you want to quit the server, use ``/q``.


	*** Scratch remote sensor server mock. Use /h for help, /q to quit ***

	Listening for client connections:  at port 42001

	> /h


	Control commands:
	  /q  - quit server
	  /h  - show this help

	Everything else will be send as is to client. Examples:
	  sensor-update "var" 42
	  broadcast "msg"

The dummy server could be especially useful if you are about to check, how your client handles bogus messages etc. 


Monitoring Sensor Client
------------------------

The monitoring sensor client is a simple client which connects to a Scratch sensor server and then just displays whatever was send by the server. This is useful if you like to "sniff" the traffic between the sensor server and any of its clients. 

To connect the monitor to a server running on localhost simply type:

	srsmon

To connect to a server running e.g. on 192.168.1.1:

	srsmon 192.168.1.1

To end the monitor, simply press CTRL+C.

_Note:_ if the server is not available at the moment the monitor is started, it keeps trying to reach that IP until it was able to connect. If the connection to the server drops, it starts trying to connect again. 

