__author__ = 'mpa'


class NotDefinedException(Exception):
    def __init__(self, message):
        """
        :param value:
        """
        super(NotDefinedException, self).__init__(message)

    def __str__(self):
        return repr(self.message)
