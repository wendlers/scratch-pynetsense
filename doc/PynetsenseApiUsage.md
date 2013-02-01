Scratch Networking Sensor Client API for Python
===============================================
15.01.2013 Stefan Wendler - [kaltpost.de] (http://kaltpost.de)


Introduction
------------

This document describes how to use the Python API for creating a Scratch Networking Sensor Client. The main thing provided by the API is a simple way to send and receive sensor value updates and broadcast messages.

For communicating with Scratch, the API implements the remote sensor protocol [as described here] (http://wiki.scratch.mit.edu/wiki/Remote_Sensors_Protocol).  

To see, how to install the API see the [README] (../README.md) that is included.


Basic API Usage
---------------

**Preparations**

Before you start using the API, make sure, Scratch is running, and the remote sensor protocol is activated (by using the right click menu on one of the sensor blocks). For a more detailed description of how to [enable/use remote sensors] (http://wiki.scratch.mit.edu/wiki/Remote_Sensor_Connections) see the Scratch Wiki.


**Create a new RemoteSensor**

First, the remote sensor module needs to be imported:

	from scratch.remote sensor import RemoteSensor 

Now, a new `RemoteSensor` instance needs to be created. If you intend to connect to a Scratch instance running on the same machine as your API program, the host and port parameters could be omitted:

	# Remote sensor connected to default host/port (localhost:42001)
	rs = RemoteSensor()
	rs.connect()

To receive updates and messages, the receiver thread needs to be started:

	# Start receiver thread
	rs.start()
	

**Using Sensor Values**

Each sensor value is represented by a variable. To introduce a new variable, or assign a new value to a already introduced variable, just assign the desired value to it in the same way as you would do for a class attribute:

	# Create new sensor variable 'a', set value to 1. This will result
    # in a 'sensor-update' message sent to Scratch sensor server. 
	rs.values.a = 1 

	# Create an other variable
	rs.values.b = 0.2 

	# An yet an other ...
	rs.values.x = "dynamic sensor-update"

_Note:_ one could use `int`, `float` and `string` as a right-value for a sensor variable. 

At the moment you introduce a new variable it is known to the Scratch sensor server. If a variable known to the server is modified form within Scratch, an sensor-update message is sent to all the connected clients. The python API listens for this messages, and updates the values for already known variables, or creates new variables for not known variables. This, when accessing the value of a variable, it will nor necessarily contain the value you wrote in earlier, but the value last published by the server. 


**Broadcast Messages**

To sent a broadcast message use the following call:

	# Broadcast a message ...
	rs.bcastMsg('foobar')


**Register Call-back Handlers for incoming Messages**

To get notified about incoming broadcast messages or variable updates, register call back handlers:

	from scratch.remote sensor import RemoteSensor 

	def updateHandler(var, val):
		'''
		Handler called for incoming sensor-updates ...
		'''
		print("-> received update: %s = %s" % (var, val))

	def messageHandler(t, msg):
		'''
		Handler called for incoming broadcast messages ... 
		'''
		print("-> received message: %s" % msg)

	# Remote sensor connected to default host/port (localhost:42001)
	rs = RemoteSensor()
	rs.connect()
	
	# Register call back handler for sensor-updates
	rs.updateHandler  = updateHandler

	# Register call back handler for broadcast messages
	rs.messageHandler = messageHandler
	
	# Start receiver thread
	rs.start()
	
	# Receiver thread is a daemon thread, thus we need to make sure that the main 
	# program does not exit while we are note done ...
	raw_input('Press Enter to quit...\n')

Now, every time a variable gets updated or a new message is received, the corresponding handler is called.


Using the Wrapper Framework
--------------------------

TODO
