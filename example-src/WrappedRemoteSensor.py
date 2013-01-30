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

	def __init__(self, args = {}):
		'''
		Create a new instance of the monitoring remote sensor. 

		@param	args	arguments for the sensor: host and port.
		'''

		logging.info("WrappedRemoteSensor initialized")
		logging.debug("Wrapper arguments: %s" % args)

		self.__args = args

		host = DEFAULT_HOST

		if self.__args.has_key('host'):
			host = self.__args['host']

		port = DEFAULT_PORT

		if self.__args.has_key('port'):
			try:
				port = int(self.__args['port'])
			except:
				logging.warn("Invalid port [%s] ignored" % self.__args['port'])

		RemoteSensor.__init__(self, host, port)

	def __readProcMem(self):
		'''
		Read memory info from proc filesystem (memtotal and memfree). If the
		value changed, send a sensor-update message to the server.
		'''
		
		try:

			f = open('/proc/meminfo', 'r')
			lines = f.readlines()
			f.close()

			for l in lines:
				w = l.split(':')
				k = w[0].strip().lower()
				v = int(w[1].strip().split(' ')[0])

				changed = False

				# this are the only field we are interested in
				if k in [ 'memtotal', 'memfree']:
					try:
						# if value is unchanged, don't update it
						if self.values.get(k) == v:
							continue
					except:
						pass

					changed = True
					self.values.set(k, v)

				if changed:
					self.bcastMsg('input-changed')

		except Exception as e:
			logging.error(e)

	def serveForever(self):
		'''
		The remote seonsor server loop.
		'''

		logging.info("WreppedRemoteSensor entering server loop")

		hbCounterMax = 50
		hbCounter 	 = 0

		try:

			self.connect(True)
			self.start()

			while True:

				try:
					time.sleep(0.1)

					hbCounter = hbCounter + 1

					# read meminfo from proc filesystem
					self.__readProcMem()

					if hbCounter == hbCounterMax:
						hbCounter = 0
						self.bcastMsg('heartbeat-wrap')

				except socket.error as e:
					logging.warn("Lost connection to Scratch server!")
					self.connect(True)

				except KeyboardInterrupt:
					break
			
		except Exception as e:
			logging.error(e)

