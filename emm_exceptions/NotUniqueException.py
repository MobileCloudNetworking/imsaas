__author__ = 'mpa'


class NotUniqueException(Exception):
    def __init__(self, message):
        """
        :param value:
        """
        super(NotUniqueException, self).__init__(message)

    def __str__(self):
        return repr(self.message)
