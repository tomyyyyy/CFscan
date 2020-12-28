import threading
import time
import queue


def producer():
    count = 1
    while 1:
        q.put('No.%i' % count)
        print('Producer put No.%i' % count)
        time.sleep(3)
        count += 1


def customer(name):
    while 1:
        print('%s get %s' % (name, q.get()))
        time.sleep(0.1)


q = queue.Queue(maxsize=5)
p = threading.Thread(target=producer, )
c = threading.Thread(target=customer, args=('jack', ))
p.start()
c.start()
p.join()
c.join()

print("dddddd")