__author__ = 'lto'


class NotFoundException(Exception):
    def __init__(self, message):
        """
        :param value:
        """
        super(NotFoundException, self).__init__(message)

    def __str__(self):
        return repr(self.message)

