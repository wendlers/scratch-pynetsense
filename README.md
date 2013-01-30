Scratch Networking Sensor Client Library for Python
===================================================
15.01.2013 Stefan Wendler
sw@kaltpost.de


Introduction
------------

This python library provides a simple to use API for implementing [Scratch] (http://scratch.mit.edu/) networking sensor clients. For communicating with Scratch, the [remote sensor protocol is used] (http://wiki.scratch.mit.edu/wiki/Remote_Sensors_Protocol).  

From the Scratch Wiki:

	The experimental extension feature is enabled using the right-button menu 
	on one of the two sensor blocks. When remote sensors are enabled, Scratch 
	listens for connections on port 42001.

	Once a connection is established, messages are sent in both directions 
	over the socket connection.

_Note:_ For a more detailed description of how to [enable/use remote sensors] (http://wiki.scratch.mit.edu/wiki/Remote_Sensor_Connections) see the Scratch Wiki.

In other words, this means, that one could share global Scratch variables among all remote sensor clients connected to Scratch. The same is true for Scratch messages: they are broadcasted to all clients. For example: 

* A remote sensor client instance connects to scratch.
* The user defines a global variable X in Scratch and assigns the value 1 to it.
* This results in a sensor update message send to all clients notifying them, that there is a variable X with a value of 1 assigned to it.

_Note:_ it is also possible that the client introduces a new variable and assigns a value to it. The variable will be  introduced to Scratch by an update message.

An update message is sent every time the value of the variable changed  by the client or by the server (Scratch).

Also messages could be sent from Scratch to remote sensors and vice versa. 

Beside providing a simple API to manage messages and variables, a wrapper framework is provided. The wrapper framework helps with implementing sensor clients that run in the background as daemons. Currently there is a full featured wrapper included for wrapping the GPIOs of an Raspberry Pi into an Scratch remote sensor client. This allows one to access the GPIOs of the Pi from Scratch by simply setting/getting some global variables.

Further Readings
----------------

* [Use the Raspberry Pi GPIO Remote Sensor Client] (https://github.com/wendlers/scratch-pynetsense/blob/master/doc/RPiGPIORemoteSensor.md)
* [Write a Sensor Client by Using the API] (https://github.com/wendlers/scratch-pynetsense/blob/master/doc/PynetsenseApiUsage.md)

* [Using the Tools that come with this API] (https://github.com/wendlers/scratch-pynetsense/blob/master/doc/PynetsenseTools.md)


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

	. setenv.sh
	python example-src/<ExampleToRun>

