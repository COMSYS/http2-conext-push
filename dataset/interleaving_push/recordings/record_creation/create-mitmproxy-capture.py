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


def start_proxy(port, logfile):
    pv = subprocess.Popen(
        ["mitmdump","--version"],stdout=subprocess.PIPE)
    out, _ = pv.communicate()

    assert "Mitmproxy version: 2" in out
    #"--insecure",
    p = subprocess.Popen(
        ["mitmdump","-q", "-w", str(logfile), "-p", str(port)])
    time.sleep(1.0)  # give the guy it some time to shine and grow
    #p = ''
    return p

def stop_proxy(p):
    if p is not None:
        # pass
        print "Waiting for the Proxy to shut down..."
        time.sleep(2.0)
        p.terminate()
        return p.wait()

parser = ArgumentParser()
parser.add_argument('--browsertime-dir',default='~/Projects/browsertime', type=str, help='installation of browsertime')
parser.add_argument('input_locations',type=str,help="csv file with identifier;urltovisit")
parser.add_argument('destination',type=str,help="destination_dir")
args = parser.parse_known_args()
passthrough = " ".join(args[1])


print "Loading Domains..."
all_domains = []
with open(args[0].input_locations) as fd:
    for line in fd:
        identifier , url = line.rstrip().split(",")
        all_domains.append((identifier,url))


chosen_domains = []
domains_with_target = {}
domains_tried = set()
util.fs.ensure_dir_exists(os.path.join(args[0].destination,'logs/'))
util.fs.ensure_dir_exists(os.path.join(args[0].destination,'mm-capture/'))

topidx = 0

while (len(domains_tried)<len(all_domains)):

    next_domain_identifier = all_domains[topidx][0]
    url = all_domains[topidx][1]
    topidx += 1


    domains_tried.add(next_domain_identifier)
    
    util.fs.ensure_dir_exists(os.path.join(args[0].destination,'mitmproxy/'))

    capture_dir = os.path.join(args[0].destination,'mitmproxy/',next_domain_identifier)
    
    outdir = os.path.join(args[0].destination,'logs/',next_domain_identifier+'/')
    
    PROXY_PORT = 1523
    proxy = start_proxy(PROXY_PORT,capture_dir)
    try:
        runner_cmdstring = 'python ../../code/runner/bt_case_runner.py --strategy push --enable-video --enable-speedindex --restart-attempts 0 --proxy localhost:'+str(PROXY_PORT)+' --runs 1 --browsertime-dir '+args[0].browsertime_dir+' '+passthrough+' '+url+' '+outdir
        print runner_cmdstring
        run_netloc_process = subprocess.Popen(runner_cmdstring, shell=True)
        run_netloc_process.wait()
    finally:
        stop_proxy(proxy)

    success = False
    harfile = os.path.join(outdir,'push/browsertime.har.gz')
    if os.path.isfile(harfile) and  os.path.isfile(os.path.join(outdir,'push/browsertime.har.gz')):
        har = None
        with gzip.open(harfile) as fd:
            har = json.load(fd)

        #print har
        
        #advance to last redirect
        last_entry = None
        for entry in har['log']['entries']:
            last_entry = entry
            redirect = entry['response']['redirectURL'] 
            if redirect:
                if redirect.startswith('http://'):
                    break
            else:
                if entry['response']['status'] != 200:
                    break
                else:
                    success = True
                    break
        
    print "FINAL _URL IS: "
    pprint.pprint(last_entry['request']['url']) #TODO TODO GEt final redirect

    if not success:
        os.remove(capture_dir)
        shutil.rmtree(outdir)
    else:
        domains_with_target[next_domain_identifier] = {'after_redirects': last_entry['request']['url']}
        chosen_domains.append(next_domain_identifier)
        print "Have captured ", len(chosen_domains), " https:// enabled domains."

with gzip.open(os.path.join(args[0].destination,'logs/domains.txt.gz'),'wb') as fd:
    for domain in chosen_domains:
        fd.write(domain+"\n")

with gzip.open(os.path.join(args[0].destination,'logs/redirect_targets.csv.gz'),'wb') as fd:
    for identifier in domains_with_target.iterkeys():
        fd.write(identifier+','+domains_with_target[identifier]['after_redirects']+"\n")

print "Done."
