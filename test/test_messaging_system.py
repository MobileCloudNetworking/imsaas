from random import random
import threading
import unittest
import time
from msg_utils.MessagingEntities import MessageObject, Action
from msg_utils.zeromq_agent import Publisher, Subscriber
import logging
import os

__author__ = 'lto'

logger = logging.getLogger('EMMLogger')

PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

rec = None


class ThreadSender(threading.Thread):
    def __init__(self, mo):
        super(ThreadSender, self).__init__()
        self.mo = mo

    def run(self):
        pub = Publisher(ip='*', port=5556, filter='filter')
        # zeroMQ needs some time after the publisher register and the send of the message
        # this sleep is only for testing purposes
        time.sleep(0.5)
        pub.send(self.mo)
        logger.debug("Sent %s" % self.mo)


class MessagingTest(unittest.TestCase):
    def test_pub_sub(self):
        # messaging system are hard to test doing it 10 times reduces the possibilities of errors
        for i in range(10):
            mo = MessageObject(message='' + str(random()), action=Action.start)

            sub = Subscriber(ip='localhost', port=5556, filter='filter')

            sen = ThreadSender(mo)
            sen.start()

            sen.send = True

            d = sub.receive()
            logger.debug("received: %s" % d)

            self.assertEqual(d.message, mo.message)
            self.assertEqual(d.action, mo.action)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s_%(process)d:%(pathname)s:%(lineno)d [%(levelname)s] %(message)s',
                        level=logging.DEBUG)
    logger = logging.getLogger("EMMLogger")
    handler = logging.FileHandler('%s/logs/%s.log' % (PATH, os.path.basename(__file__)))
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s_%(process)d:%(pathname)s:%(lineno)d [%(levelname)s] %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    unittest.main()

