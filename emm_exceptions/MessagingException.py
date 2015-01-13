__author__ = 'lto'


class MessagingException(Exception):
    def __init__(self, message):
        """
        :param value:
        """
        super(MessagingException, self).__init__(message)

    def __str__(self):
        return repr(self.message)