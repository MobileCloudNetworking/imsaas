import time
import zmq
import ast
import logging
from emm_exceptions.MessagingException import MessagingException
from msg_utils.MessagingEntities import Action, MessageObject

__author__ = 'lto'

logger = logging.getLogger('EMMLogger')


from abc import ABCMeta, abstractmethod


class ZeroMQSender(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def send(self, obj_msg):
        logger.error("send: obj_msg")


class ZeroMQReceiver(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def receive(self, obj_msg):
        logger.error("receive: obj_msg")


class Publisher(ZeroMQSender):

    def __init__(self, port, ip, protocol='tcp', filter=''):
        """
        :param port:
        :param ip:
        :param protocol:    can be
                            tcp
                                unicast transport using TCP, see zmq_tcp(7)
                            ipc
                                local inter-process communication transport, see zmq_ipc(7)
                            inproc
                                local in-process (inter-thread) communication transport, see zmq_inproc(7)
                            pgm, epgm
                                reliable multicast transport using PGM, see zmq_pgm(7)
        :return:
        """
        context = zmq.Context()

        # Define the socket using the "Context"
        self.filter = filter
        self.sock = context.socket(zmq.PUB)
        self.sock.bind("tcp://127.0.0.1:5680")

    def send(self, obj_msg):

        # Message [prefix][message]
        message = "%s#:#%s" % (self.filter, obj_msg.__dict__)
        self.sock.send(message)


class Subscriber(ZeroMQReceiver):

    def receive(self):
        message = self.sock.recv()
        obj = MessageObject(**ast.literal_eval(message.split('#:#')[1]))
        logger.debug('Received: %s ' % obj)
        return obj

    def __init__(self, port, ip, protocol='tcp', filter=''):
        #  Socket to talk to server
        context = zmq.Context()

        # Define the socket using the "Context"
        self.sock = context.socket(zmq.SUB)

        # Define subscription and messages with prefix to accept.
        self.sock.setsockopt(zmq.SUBSCRIBE, filter)
        self.sock.connect("tcp://127.0.0.1:5680")