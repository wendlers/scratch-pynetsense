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

import logging

from scratch.remotesensor import RemoteSensor 

try:
	# Configure logging for RemoteSensor to show DEBUG messages ...
	logging.basicConfig(
		level=logging.DEBUG,
		format='%(asctime)s %(levelname)-8s %(message)s',
		datefmt='%m-%d %H:%M',
	)

	# Remote sensor connected to default host/port (localhost:42001)
	rs = RemoteSensor()
	rs.connect()

	# Start receiver thread
	rs.start()
	
	# Create new sensor variable 'a', set value to 1. This will tesult
    # in a 'sensor-update' message sent to Scratch sensor server. 
	rs.values.a = 1 

	# Create an other variable
	rs.values.b = 0.2 

	# An yet an other ...
	rs.values.x = "dynamic sensor-update"

	# Broadcast a message ...
	rs.bcastMsg('foobar')

	raw_input('Press Enter to quit...\n')
	
except Exception as e:
	print(e)
