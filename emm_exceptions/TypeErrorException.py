__author__ = 'mpa'


class TypeErrorException(Exception):
    def __init__(self, message):
        """
        :param value:
        """
        super(TypeErrorException, self).__init__(message)

    def __str__(self):
        return repr(self.message)
