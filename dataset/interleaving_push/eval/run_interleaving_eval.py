from argparse import ArgumentParser
import gzip
import errno
import sys
import os
import subprocess
sys.path.append(os.path.join(os.path.dirname(__file__), '../code'))
import util.fs
from common import PUSH_STRATEGY_JSON_FILENAMES, AVAILABLE_SITES


DSL_DOWNSTREAM=16000
DSL_UPSTREAM=1000
DSL_LATENCY=25


parser = ArgumentParser(prog='eval_runner')

parser.add_argument('--runs', type=int, default=5)
parser.add_argument('--browsertime-dir', type=str, required=True)

parser.add_argument('--replay-dir', type=str, required=True)
parser.add_argument('--strategy-dir', type=str, required=True)
parser.add_argument('--mergefile-dir', type=str, required=True)
parser.add_argument('--logs-dir', type=str, required=True)
parser.add_argument('--destination', type=str, required=True)

args = parser.parse_args()

CASE_RUNNER_PATH = os.path.join(os.path.dirname(__file__), '../code/runner/bt_case_runner.interleaving.py')

for site in AVAILABLE_SITES:
    for strategy in PUSH_STRATEGY_JSON_FILENAMES.iterkeys():
        
        print "Running", strategy
        
        replay_dir = os.path.join(args.replay_dir,site)
        push_strategy_path = os.path.join(args.strategy_dir,site+"/"+PUSH_STRATEGY_JSON_FILENAMES[strategy])
        mergefile = os.path.join(args.mergefile_dir,site+"/mergelist")
        #url to query?
        urlfile = os.path.join(args.logs_dir,site+"/requested_url.gz")
        with gzip.open(urlfile) as fd:
            url = fd.readline().strip()

        outdir = os.path.join(args.destination,site+'/'+strategy)
        passthrough = ''

        runner_cmdstring = 'python '+CASE_RUNNER_PATH+' --strategy push --enable-video --enable-speedindex --restart-attempts 0 --runs '+ \
                        str(args.runs) + \
                        ' --browsertime-dir ' + args.browsertime_dir +\
                        ' --mahimahi-replay ' +\
                        ' --mahimahi-replay-policy same-ip-mergefile' + \
                        ' --mahimahi-replay-dir ' + replay_dir +  \
                        ' --mahimahi-replay-strategy ' + push_strategy_path +  \
                        ' --mahimahi-replay-mergefile ' + mergefile + \
                        ' --mahimahi-shapingdelay '+ str(DSL_LATENCY) + \
                        ' --mahimahi-shapinguplink '+ str(DSL_UPSTREAM) + \
                        ' --mahimahi-shapingdownlink '+ str(DSL_DOWNSTREAM) + \
                        passthrough + ' "'+url+'" '+outdir
        
        print runner_cmdstring
        run_netloc_process = subprocess.Popen(runner_cmdstring, shell=True)
        run_netloc_process.wait()
    
