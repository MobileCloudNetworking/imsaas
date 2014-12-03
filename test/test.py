__author__ = 'gca'

import os
from so.util import util

def main():
    print os.getcwd()

    stream = open("../../data/ims.yaml",'r')
    t = util.stack_parser(stream)
    print t

if __name__ == "__main__":
    main()