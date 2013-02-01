##
# This file is part of the Scratch Remote Sensor (SRS) Library project
#
# Copyright (C) 2012 Stefan Wendler <sw@kaltpost.de>
#
# The SRS Library is free software; you can redistribute 
# it and/or modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
#  version 2.1 of the License, or (at your option) any later version.
#
#  SRS Library is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Lesser General Public License for more details.
# 
#  You should have received a copy of the GNU Lesser General Public
#  License along with the JSherpa firmware; if not, write to the Free
#  Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
#  02111-1307 USA.  
##

'''
This file is part of the Scratch Remote Sensor Library project
'''

import time
import socket
import logging

from scratch.remotesensor import RemoteSensor, DEFAULT_HOST, DEFAULT_PORT 

class WrappedRemoteSensor(RemoteSensor):
	'''
	This example shows how to write a baic wrapped remote sensor. It reads
	"/proc/meminfo" and parses out the values for "memtotal" and "memfree".
	Each time one of this values changes, a sensor-update is send to the 
	server. 

	To start this sensor, pass it as a wrapper to the wrapper daemon:

	source setenv.sh
	python src/scratch/wrappers/daemon.py --foreground --loglevel DEBUG \
		   --wrap WrappedRemoteSensor#WrappedRemoteSensor start	
	'''

	__args = None 

	# name used e.g. for heartbeat
	name = "wrap"

	def __init__(self, myArgs = {}):
		'''
		Create a new instance of the monitoring remote sensor. 

		@param	myArgs	arguments for the sensor: host and port.
		'''

		RemoteSensor.__init__(self, args = myArgs)

	def worker(self):
		'''
		Read memory info from proc filesystem (memtotal and memfree). If the
		value changed, send a sensor-update message to the server.
		'''
		
		try:

			f = open('/proc/meminfo', 'r')
			lines = f.readlines()
			f.close()

			changed = False

			for l in lines:
				w = l.split(':')
				k = w[0].strip().lower()
				v = int(w[1].strip().split(' ')[0])

				# this are the only field we are interested in
				if k in [ 'memtotal', 'memfree']:
					if self.values.set(k, v):
						changed = True

			if changed:
				self.bcastMsg('input-changed')

		except Exception as e:
			logging.error(e)

