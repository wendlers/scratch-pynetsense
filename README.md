Scratch Networking Sensor Client Library for Python
===================================================
15.01.2013 Stefan Wendler
sw@kaltpost.de

This python library provides a simple to use API for implementing [Scratch] (http://scratch.mit.edu/) networking sensor clients. For communicating with Scratch, the [remote seonsor protocol is used] (http://wiki.scratch.mit.edu/wiki/Remote_Sensors_Protocol).  

From the Scratch Wiki:

	The experimental extension feature is enabled using the right-button menu 
	on one of the two sensor blocks. When remote sensors are enabled, Scratch 
	listens for connections on port 42001.

	Once a connection is established, messages are sent in both directions 
	over the socket connection.

In other words, this means, that one could share global Scratch variables amoung all remote sensor clients connected to Scratch. The same is true for Scratch messages: they are broadcasted to all clients. For example: 

* A remote sensor client instance connectes to scratch
* The user defines a global variable X in Scratch and assigns the value 1 to it
* Thie imidiateley results in a sensor update message sent to the client notifying it, that there is a varaibale X with a value of 1 assigned to it.

Note: it is also posible that the client introduces a new variable and assignes a value to it. The variable will be imidiately introduced to Scratch by an update message.

An update message is sent every time the value of the variable changed eighter by the client or by the server (Scratch).

Also messages could be sent from Scratch to remote sensors and vice versa. 


Project Directory Layout
------------------------

* `bin`				Shell-Script wrappers to start dummy server
* `example-src`		Examples
* `LICENSE`			License information 
* `README.md`		This README
* `src`				Sources of this library
* `setenv.sh`		Set PYTHONPATH for testing
* `setup.py`		Setup script to install/distribute


Prerequisites
-------------

To use this Scratch remote sensor protocol library, Scratch in a version >= 1.3 is needed. 
If you are going to run Scratch and the remote sensors on different machines, make sure
the machines are accessible through networking.  


Install the Library
-------------------

To install the library issue the following command in the top-level project directory:

	python setup.py install

Alternatively you could place the "scratch" folder from "src" to a directory of
your choice and make your PYTHONDIR point to it. E.g. if you copied "src/scratch"
to "~/python/scratch":

	export PYTHONPATH=~/python/scratch


Examples
--------

Some examples are located under "example-src/". On the command line, 
you could run them after you installed the library like this:

	python example-src/<ExampleToRun>

If you prefer running the examples from the project directory (without installing the library), you 
could do the following:

	. setup.sh
	python example-src/<ExampleToRun>

Note: you could use the examples against the dummy server implementation provided with this library. To start the dummy server, issue the following from the projects top-level directory (before running the examples):

	./bin/rsdummysrv


API Usage
---------

Before you start using the API, make sure, Scratch is running, and the remote sensor protocol is activated (by using the right click menu on one of the sensor blocks). 

First, the remote sensor module neeeds to be imported:

	from scratch.remotesensor import RemoteSensor 

Now, a new `RemoteSensor` instance needs to be created. If you intend to connect to a Scratch instance running on the same machine as your API programm, the host and port parameters could be omitted:

	# Remote sensor connected to default host/port (localhost:42001)
	rs = RemoteSensor()

To receive updates and messges, the receiver thread needs to be started:

	# Start receiver thread
	rs.start()
	
To introduce a new varaible, or assigne a new value to a already introduced variable, just assign the desired value to it:

	# Create new sensor variable 'a', set value to 1. This will tesult
    # in a 'sensor-update' message sent to Scratch sensor server. 
	rs.values.a = 1 

	# Create an other variable
	rs.values.b = 0.2 

	# An yet an other ...
	rs.values.x = "dynamic sensor-update"

Note: one could use `int`, `float` and `string` to a sensor variable. 

To sent a message use the following:

	# Broadcast a message ...
	rs.bcastMsg('foobar')

To get notified about incoming broadcast messages or variable updates, register callback handlers:

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

	# Register callback handler for sensor-updates
	rs.updateHandler  = updateHandler

	# Register callback handler for broadcast messages
	rs.messageHandler = messageHandler
	
	# Start receiver thread
	rs.start()
	
Now, every time a variable gets updated or a new message is received, the coresponding handler is called.

