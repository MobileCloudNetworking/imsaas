__author__ = 'mpa'


class InvalidInputException(Exception):
    def __init__(self, message):
        """
        :param value:
        """
        super(InvalidInputException, self).__init__(message)

    def __str__(self):
        return repr(self.message)
