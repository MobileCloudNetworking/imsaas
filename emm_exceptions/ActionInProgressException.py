__author__ = 'mpa'


class ActionInProgressException(Exception):
    def __init__(self, message):
        """
        :param value:
        """
        super(ActionInProgressException, self).__init__(message)

    def __str__(self):
        return repr(self.message)
__author__ = 'mpa'
