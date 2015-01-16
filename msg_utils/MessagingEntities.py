__author__ = 'lto'


class MessageObject:
    def __init__(self, **kwargs):
        self.message = kwargs['message']
        self.action = kwargs['action']

    def __str__(self):
        res = 'MessageObject: [ '
        res += 'Action=%s, ' % self.action
        res += 'Message=%s ]' % self.message
        return res


def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    reverse = dict((value, key) for key, value in enums.iteritems())
    enums['reverse_mapping'] = reverse
    return type('Enum', (), enums)


Action = enum(init='init', install='install', add_relation='add_relation', start='start', error='error',
              restart='restart')


class RegisterUnitMessage:
    def __init__(self, **kwargs):
        self.action = kwargs['action']
        self.hostname = kwargs['hostname']
        self.ws = kwargs['ws']

    def __str__(self):
        res = 'RegisterUnitMessage: [ '
        res += 'Action=%s, ' % self.action
        res += 'ws=%s, ' % self.ws
        res += 'hostname=%s ]' % self.hostname
        return res