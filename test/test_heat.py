__author__ = 'mpa'

from clients import heat

if __name__ == '__main__':
    heatclient = heat.Client()
    response = heatclient.list_resources(stack_id='c3fb9632-a791-4c55-be04-e028536a205c')
    print "list: %s" % response

    response = heatclient.show(stack_id='c3fb9632-a791-4c55-be04-e028536a205c')

    print "stack: %s" % response.get('stack_status')

