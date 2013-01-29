Scratch Networking Sensor Client Library for Python
===================================================
15.01.2013 Stefan Wendler
sw@kaltpost.de

This python library provides a simple to use API for implementing [Scratch] (http://scratch.mit.edu/) networking sensor clients. For communicating with Scratch, the [remote sensor protocol is used] (http://wiki.scratch.mit.edu/wiki/Remote_Sensors_Protocol).  

From the Scratch Wiki:

	The experimental extension feature is enabled using the right-button menu 
	on one of the two sensor blocks. When remote sensors are enabled, Scratch 
	listens for connections on port 42001.

	Once a connection is established, messages are sent in both directions 
	over the socket connection.

In other words, this means, that one could share global Scratch variables among all remote sensor clients connected to Scratch. The same is true for Scratch messages: they are broadcasted to all clients. For example: 

* A remote sensor client instance connects to scratch.
* The user defines a global variable X in Scratch and assigns the value 1 to it.
* This  results in a sensor update message sent to the client notifying it, that there is a variable X with a value of 1 assigned to it.

Note: it is also possible that the client introduces a new variable and assigns a value to it. The variable will be  introduced to Scratch by an update message.

An update message is sent every time the value of the variable changed  by the client or by the server (Scratch).

Also messages could be sent from Scratch to remote sensors and vice versa. 


Further Readings
----------------

* [Use the Raspberry Pi GPIO Remote Sensor] (./wendlers/scratch-pynetsense/blob/master/doc/PynetsenseApiUsage.md)
* [Write a Sensor Client by Using the API] (./wendlers/scratch-pynetsense/blob/master/doc/PynetsenseApiUsage.md)


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

	python src/scratch/rsdummysrv.py

