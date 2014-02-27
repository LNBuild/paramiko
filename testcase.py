import sys
import os
import time

import paramiko
import threading
import Queue

print 'Paramiko module:', paramiko.__file__
paramiko.util.log_to_file('paramiko.log')

a = paramiko.Agent()
print a.get_keys()

username = os.environ['USER']
print username

def auth_worker(q):
	while True:
		t = q.get()
		print 'Authenticating', t
		for key in a.get_keys():
			try:
				print 'Trying key', key.name
				t.auth_publickey(username, key)
			except paramiko.AuthenticationException:
				print 'Auth failed'
				pass
			except Exception as e:
				print 'Auth_Publickey', repr(e)
			if t.is_authenticated():
				break
		q.task_done()

auth_queue = Queue.Queue()

transports = []
for x in xrange(int(sys.argv[1])):
	t = paramiko.Transport (('127.0.0.1', 22))
	print t
	t.connect()
	transports.append(t)

print '%d transports connected to 127.0.0.1' % len(transports)

for x in xrange(int(sys.argv[2])):
	thr = threading.Thread(target = auth_worker, args = (auth_queue,))
	thr.setDaemon(True)
	thr.start()

for x in transports:
	auth_queue.put(x)

auth_queue.join()
print transports
