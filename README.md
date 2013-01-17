scratch networking sensor client library for python
===================================================
15.01.2013 Stefan Wendler
sw@kaltpost.de

This python library provides a simple to use client implementation for implementing scratch networking sensors 

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

