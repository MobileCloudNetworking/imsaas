__author__ = 'lto'


class MessageObject:
    def __init__(self, **kwargs):
        self.message = kwargs['message']
        self.action = kwargs['action']

    def __str__(self):
        str = 'MessageObject: [ '
        str += 'Action=%s, ' % self.action
        str += 'Message=%s ]' % self.message
        return str


def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    reverse = dict((value, key) for key, value in enums.iteritems())
    enums['reverse_mapping'] = reverse
    return type('Enum', (), enums)


Action = enum(init='init', install='install', add_relation='add_relation', start='start', error='error',
              restart='restart')
