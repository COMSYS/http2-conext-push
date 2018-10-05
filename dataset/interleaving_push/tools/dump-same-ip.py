import gzip
import os
import subprocess
import random
import shutil
import json
import time
import pprint
import argparse
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../code'))

import util.fs
import util.strategy



def main():
    parser = argparse.ArgumentParser(description='Generates an index.html one js with varing size')
    parser.add_argument('netlog',type=str, help="Chrome Netlog")
    parser.add_argument('har',type=str, help="Browsertime HAR")
    args = parser.parse_args()

    if not os.path.exists(args.netlog):
        print "NOT FOUND!", args.netlog


    if not os.path.exists(args.har):
        print "NOT FOUND!", args.har

    browsertime_har = None
    with gzip.open(args.har) as fd:
        browsertime_har = json.load(fd)


    after_redirects, same_origin_in_order = util.strategy.getH2DependencyFromNetlog(args.netlog,browsertime_har)


    print same_origin_in_order


if __name__ == '__main__':
    main()
