import gzip
import os
import subprocess
import random
import shutil
import json
import time
import pprint
from argparse import ArgumentParser
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../code'))
import util.fs

parser = ArgumentParser()
parser.add_argument('input_locations',type=str,help="csv file with identifier;page_of_html_to_grab")
parser.add_argument('recording_dir',type=str,help="recording_dir")
parser.add_argument('destination_dir',type=str,help="destination_dir")
args = parser.parse_args()


print "Loading Domains..."
all_domains = []
with gzip.open(args.input_locations) as fd:
    for line in fd:
        identifier , url = line.rstrip().split(",")
        all_domains.append((identifier,url))


for identifier, url in all_domains:
    output_dir = os.path.join(args.destination_dir,'html/{}'.format(identifier))
    util.fs.ensure_dir_exists(output_dir)
    
    capture_file = os.path.join(args.recording_dir,identifier)
    output_file = os.path.join(output_dir,'captured.gz')

    print identifier
    pv = subprocess.Popen(
        'mitmdump -n -q -s "mitm2html.py {}" -r {} | gzip > {}'.format(url,capture_file,output_file),
        shell=True)
    pv.communicate()

