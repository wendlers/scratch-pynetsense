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

import sys
import os
import time
import atexit
import argparse
import logging
import socket

from signal import SIGTERM 

class Daemon:
	'''
	Provide Unix Daemon functionality used to start a certain wrapper in background. 	
	'''

	stdin			= None
	stdout 			= None
	stderr			= None
	pidfile			= None
	wrapargs		= None

	def __init__(self, wrapargs = {}, pidfile = '/var/run/srsd.pid', stdin = '/dev/null', stdout = '/dev/null', stderr = '/dev/null'):
		'''
		Construct a new daemon instance.

		@param	wrapargs	argument dictionary passed to wrappers constructor
		@param	pidfile		pidfile to use for the daemon
		@param	stdin		where to redirect stdin to 
		@param	stdout		where to redirect stdout to
		@param	srderr		where to redirect stderr to
		'''

		self.wrapargs		= wrapargs
		self.stdin 			= stdin
		self.stdout 		= stdout
		self.stderr 		= stderr
		self.pidfile 		= pidfile

	def daemonize(self):
		'''
		Operation called for daemonizing the current process (does the double fork magic).
		'''

		try: 

			pid = os.fork() 
			if pid > 0:
				# exit first parent
				sys.exit(0) 

		except OSError, e: 

			sys.stderr.write("Fork failed: %d (%s)\n" % (e.errno, e.strerror))
			sys.exit(1)
	
		# decouple from parent environment
		os.chdir("/") 
		os.setsid() 
		os.umask(0) 
	
		# do second fork
		try: 

			pid = os.fork() 
			if pid > 0:
				# exit from second parent
				sys.exit(0) 

		except OSError, e: 

			sys.stderr.write("Fork failed: %d (%s)\n" % (e.errno, e.strerror))
			sys.exit(1) 
	
		# redirect standard file descriptors
		sys.stdout.flush()
		sys.stderr.flush()

		si = file(self.stdin, 'r')
		so = file(self.stdout, 'a+')
		se = file(self.stderr, 'a+', 0)

		os.dup2(si.fileno(), sys.stdin.fileno())
		os.dup2(so.fileno(), sys.stdout.fileno())
		os.dup2(se.fileno(), sys.stderr.fileno())
	
		# write pidfile
		atexit.register(self.delpid)
		pid = str(os.getpid())
		file(self.pidfile,'w+').write("%s\n" % pid)

	def delpid(self):
		'''
		Delete pidfile.
		'''

		os.remove(self.pidfile)

	def start(self):
		'''
		Start a new daemon instance.
		'''

		# Check for a pidfile to see if the daemon already runs
		try:

			pf = file(self.pidfile,'r')
			pid = int(pf.read().strip())
			pf.close()

		except IOError:

			pid = None
	
		if pid:

			sys.stderr.write("Pidfile %s already exist. Daemon already running?\n" % self.pidfile)
			sys.exit(1)
		
		# Start the daemon
		self.daemonize()
		self.run()

	def stop(self):
		'''
		Stop a running daemon instance.
		'''

		# Get the pid from the pidfile
		try:

			pf = file(self.pidfile,'r')
			pid = int(pf.read().strip())
			pf.close()

		except IOError:

			pid = None
	
		if not pid:

			sys.stderr.write("Pidfile %s does not exist. Daemon not running?\n" % self.pidfile)
			return 

		# Try killing the daemon process	
		try:

			while 1:
				os.kill(pid, SIGTERM)
				time.sleep(0.1)

		except OSError:

			if os.path.exists(self.pidfile):
				os.remove(self.pidfile)

	def restart(self):
		'''
		Restart a daemon instance by calling stop, then start. 
		'''

		self.stop()
		self.start()

	def run(self):
		'''
		This method is run within the daemon instance. It creates a new instance of 
		the given wrapper, passes the wrapargs dictionary to it and start the wrappers
		server loop.
		'''
		
		wrap = None

		try:

			wrap = WrappedRemoteSensor(self.wrapargs)

			logging.info("WreppedRemoteSensor entering server loop")

			hbCounterMax = 50
			hbCounter 	 = 0

			wrap.connect(True)
			wrap.start()

			while True:

				try:
					time.sleep(0.1)

					hbCounter = hbCounter + 1

					# read meminfo from proc filesystem
					wrap.worker()

					if hbCounter == hbCounterMax:
						hbCounter = 0
						wrap.bcastMsg("heartbeat-%s" % wrap.name)

				except socket.error as e:
					logging.warn("Lost connection to Scratch server!")
					wrap.connect(True)

				except KeyboardInterrupt:
					break
			
		except Exception as e:
			logging.error(e)

		finally:
			del wrap

if __name__=="__main__":

	parser = argparse.ArgumentParser(description='Scratch Remote Sensor Client daemon')

	parser.add_argument('command', metavar='COMMAD', type=str, 
		help='Command to operate the daemon: start, stop, restart, rmpid')

	parser.add_argument('--foreground', dest='foreground', action='store_true', default=False, 
		help='Run in foreground, do not fork')

	parser.add_argument('--pid', dest='pidfile', metavar='FILE', default='/var/run/srsd.pid', 
		type=str, help='PID file to use')

	parser.add_argument('--log', dest='logfile', metavar='FILE', default='/var/log/srsd.log', 
		type=str, help='Logfile to use')

	parser.add_argument('--loglevel', dest='loglevel', metavar='NUMBER', default='INFO', 
		type=str, help='Loglevel to use')

	parser.add_argument('--wrap', dest='wrapper', metavar='WRAPPER', 
		default='scratch.wrappers.mon#MonitoringRemoteSensor', 
		type=str, help='Wrapper to instanciate with the daemon')

	parser.add_argument('--wrapargs', metavar='ARGS', dest='wrapargs', type=str,  
		help='Arguments to pass to wrapper instance for configuration')

	args = parser.parse_args()

	if not args.command in ['start', 'stop', 'restart', 'rmpid']:
		sys.stderr.write("Unknown command [%s]\n" % args.command)
 		sys.exit(1)
	
	# try to get logger ...
	try:
		if args.foreground:
			logging.basicConfig(
				level=args.loglevel,
				format='%(asctime)s %(name)-3s %(levelname)-8s %(message)s',
				datefmt='%m-%d %H:%M:%S'
			)
		else:
			logging.basicConfig(
				level=args.loglevel,
				format='%(asctime)s %(name)-3s %(levelname)-8s %(message)s',
				datefmt='%m-%d %H:%M:%S',
				filename=args.logfile,
				filemode='a'
			)
	except Exception as e:
		sys.stderr.write(e.__str__() + "\n")
 		sys.exit(1)

	# see if we have wrapper arguments ...
	wa = {}

	try:

		if args.wrapargs:
			al = args.wrapargs.split(':')
			
			for a in al:
				kv = a.split('=')
				wa[kv[0].strip()] = kv[1].strip()

	except Exception as e:
		sys.stderr.write("Invalid wrapper arguments: " + e.__str__() + "\n")
 		sys.exit(1)
	
	# see what command the daemon should performe ...
	d = Daemon(pidfile=args.pidfile, wrapargs=wa)

	# do we need to import the wrapper (only on start/restart)?
	if args.command == "start" or args.command == "restart":

		w = ("%s" % args.wrapper.replace('#', ' import '))

		try:

			exec("from %s as WrappedRemoteSensor" % w)

		except Exception as e:

			logging.error("Error while importing wrapper [%s]: %s\n" % (w, e))
			sys.stderr.write("Error while importing wrapper [%s]: %s\n" % (w, e))
 			sys.exit(1)
	
	if args.command == "start":

		sys.stdout.write("Starting SRS daemon\n")
		logging.info("Starting SRS daemon")
	
		if args.foreground:
			d.run()
		else:
			d.start()	

	elif args.command == "stop":

		sys.stdout.write("Stopping SRS daemon\n")
		logging.info("Stopping SRS daemon")
		d.stop()	

	elif args.command == "restart":

		sys.stdout.write("Restarting SRS daemon\n")
		logging.info("Restarting SRS daemon")

		d.restart()	

	elif args.command == "rmpid":

		sys.stdout.write("Removing stall PID: %s\n" % args.pidfile)

		if os.path.exists(args.pidfile):
			os.remove(args.pidfile)
