import pickle
from net_threads import *
from Queue import Queue
from time import sleep
import marshal

push_queue = Queue()
push_thread = PushThread(push_queue, '192.168.1.1', 9001)
push_thread.start()

pull_queue = Queue()
pull_thread = PullThread(pull_queue, 9000)
pull_thread.start()

ard_read_queue = Queue()
ard_read_thread = ArdReadThread(ard_read_queue, "/dev/ttyO1", 115200)
ard_read_thread.start()

sleep(1)

ard_write_queue = Queue()
ard_write_thread = ArdWriteThread(ard_write_queue, "/dev/ttyO1", 115200)
ard_write_thread.start()

def pulll(key,msg):
    val = 0
    i = msg.find(key) 

    if i>-1:           
        if msg[i+3] == '{': 
            j = msg.find('}',i)
            if j>i:
                val = int(float(msg[i+1+len(key):j]))
    return val

while True:
    if(pull_queue.qsize()):
        commands = marshal.loads(pull_queue.get())
        r = commands['r']
        m = commands['m']

        rstr = "R{" + str(int(r)) + "}M{" + str(int(m)) + "}"
        if r:
            print rstr
        ard_write_queue.put(rstr)

    if(ard_read_queue.qsize()):
        msg = ard_read_queue.get()

        phi = pulll('PHI', msg)
        dell = pulll('DEL', msg)
        bat = pulll('BAT', msg)
 
        telemetry = {'phi':phi,'del':dell,'bat':bat}
 
        push_queue.put(marshal.dumps(telemetry))                

    sleep(.001)