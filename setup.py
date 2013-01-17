#!/usr/bin/env python

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

from distutils.core import setup

setup(name='scratch-pynetsense',
	version='0.1',
	description='Scratch Remote Sensor Library',
	long_description='Client library for Python to use with the Scratch remote sensor protocol.',
	author='Stefan Wendler',
	author_email='sw@usherpa.org',
	url='http://www.usherpa.org/',
	license='LGPL 2.1',
	packages=['scratch'],
	platforms=['Linux'],
	package_dir = {'': 'src'}
)
