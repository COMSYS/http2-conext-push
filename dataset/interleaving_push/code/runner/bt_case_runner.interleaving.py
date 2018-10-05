import gzip
import errno
import sys
import os
import subprocess
from threading import Timer
from argparse import ArgumentParser
from urlparse import urlsplit, urlparse, urlunsplit
sys.path.append(os.path.join(os.path.dirname(__file__), '../../code'))
import util.fs



def main():

    parser = ArgumentParser(prog='bt_case_runner.interleaving.py')

    parser.add_argument(
        'input_location', type=str, help='url or netloc to contact')

    parser.add_argument(
        'destdir', type=str, help='Output Directory for results')

    parser.add_argument('--strategy', action='append',
                        help='Register a strategy to run (h1,nopush,push, etc.)')

    parser.add_argument('--prepend-url-scheme', type=str, default='https',
                        required=False, help='If the netloc has no url schema what schema to prepend? (http, default=https)')

    parser.add_argument('--browsertime-dir',type=str, required=True,help="Directory of the current browsertime installation")

    parser.add_argument('--www', action='store_true',
                        required=False, help='Prepend www. to netloc (only if not already an url)')

    parser.add_argument('--runs',
                        type=int,
                        required=False,
                        default=31,
                        help='Repetitions')

    parser.add_argument('--restart-attempts',
                        type=int,
                        required=False,
                        default=2,
                        help='How often to retry if browsertime fails to generate a har file')

    parser.add_argument('--viewport',
                        type=str,
                        default="1200x960",
                        help='What viewport to capture? Format: WIDTHxHEIGHT in px')


    parser.add_argument('--proxy', default=None, type=str, required=False, help="Browsertime Proxy")

    parser.add_argument('--enable-speedindex',
                        action="store_true",
                        help='compute speedindex metric')

    parser.add_argument('--enable-videos',
                        action="store_true",
                        help='Create videos using ffmpeg')

    parser.add_argument('--render-framebuffer',
                        action="store_true",
                        help='Render chrome in XVFB')

 
    parser.add_argument('--mahimahi-delay',type=int,default=-1) #uses mm-delay
    parser.add_argument('--mahimahi-shapingdelay',type=int,default=-1) #uses mm-shapingshell
    parser.add_argument('--mahimahi-shapinguplink',type=int,default=-1) #uses mm-shapingshell
    parser.add_argument('--mahimahi-shapingdownlink',type=int,default=-1) #uses mm-shapingshell
    
    parser.add_argument('--mahimahi-replay',action='store_true') #enables replay
    parser.add_argument('--mahimahi-replay-dir',type=str)
    parser.add_argument('--mahimahi-replay-strategy',type=str, default="noop")
    parser.add_argument('--mahimahi-replay-policy',type=str, default="same-ip")
    parser.add_argument('--mahimahi-replay-mergefile',type=str, default="noop")

    parser.add_argument('--mahimahi-record',action='store_true') #enables replay
    parser.add_argument('--mahimahi-record-dir',type=str)


    args = parser.parse_args()


    prepend_cmd = ""

    if args.mahimahi_replay:
        if args.mahimahi_replay_policy == "same-ip-mergefile":
            prepend_cmd += "mm-webreplay {} {} {} {} ".format(args.mahimahi_replay_dir, args.mahimahi_replay_strategy , args.mahimahi_replay_policy, args.mahimahi_replay_mergefile)
        else:
            prepend_cmd += "mm-webreplay {} {} {} ".format(args.mahimahi_replay_dir, args.mahimahi_replay_strategy, args.mahimahi_replay_policy)

    if args.mahimahi_record:
        prepend_cmd += "mm-webrecord {} ".format(args.mahimahi_record_dir)


    if args.mahimahi_delay != -1:
        prepend_cmd += "mm-delay {} ".format(args.mahimahi_delay)

    if args.mahimahi_shapingdelay != -1:
        prepend_cmd += "mm-shaping {} {} {} ".format(args.mahimahi_shapingdelay, args.mahimahi_shapinguplink, args.mahimahi_shapingdownlink)



    if not args.input_location.startswith("http"):
        if args.www:
            url = args.prepend_url_scheme + "://www." + args.input_location
        else:
            url = args.prepend_url_scheme + "://" + args.input_location

        netloc = target
    else:
        # we have a url
        url = args.input_location
        netloc = urlparse(args.input_location).hostname

    output_directory = args.destdir

    # use netloc as directory name, append .$ctr we have the same
    # netloc multiple times...
    if os.path.isdir(output_directory):
        appendix = 0
        while os.path.isdir(output_directory + '.' + str(appendix)):
            appendix += 1
        output_directory = output_directory + '.' + str(appendix)
    print output_directory
    util.fs.ensure_dir_exists(output_directory)

    with gzip.open(output_directory + '/requested_url.gz', 'w') as fd:
        fd.write(url)

    for runspec in args.strategy:

        binary=os.environ['CHROME_BINARY_PUSH']
        chromedriver=os.environ['CHROMEDRIVER_BINARY']

        if runspec == 'h1':
            run_scenario = 'h1'
            extra_chromeflags = ' --chrome.args="--disable-http2"'
        elif runspec == 'nopush':
            run_scenario = 'nopush'
            extra_chromeflags = ' --chrome.args="--disable-http2-push"'
        else:
            run_scenario = 'push'
            extra_chromeflags = ''

        chromerunner_strategy_output = output_directory + '/' + run_scenario
        util.fs.ensure_dir_exists(chromerunner_strategy_output)


        bt_env = os.environ.copy()

        if args.enable_speedindex is True:
            speedindexArgs = ' --speedIndex'
        else:
            speedindexArgs = ''

        if args.enable_videos is True:
            videoArgs = ' --video --xvfb --videoParams.addTimer false --videoParams.createFilmstrip false'
        else:
            videoArgs = ''

        if args.enable_videos or args.render_framebuffer:
            bt_env['BROWSERTIME_XVFB'] = 'true'

        attempts_left = len(xrange(0,args.runs,10))+args.restart_attempts
        browsertime_success = False
        
        while attempts_left > 0 and browsertime_success is False:
            current_batch_dir = chromerunner_strategy_output
            attempts_left -= 1

            proxy_args = ''
            if(args.proxy is not None):
                proxy_args += ' --chrome.args=\'--host-resolver-rules="MAP * ~NOTFOUND , EXCLUDE localhost"\''
                proxy_args += ' --chrome.args="--proxy-server=http://'+args.proxy+'"'
            

            #' --chrome.chromedriverPath ' + chromedriver + \ 
	    # collectTracingEvents wont work for my chromedriver 2.28 while the alto saxophone driver currently works ...
            #' --chrome.collectPerfLog ' + \
            #' --chrome.collectTracingEvents ' + \
            browsertime_cmdstring = prepend_cmd + args.browsertime_dir + \
                '/bin/browsertime.js '+ videoArgs + speedindexArgs + \
                ' --chrome.binaryPath '+ binary + \
                ' -n ' +str(args.runs) + \
                proxy_args + \
                ' --preURL https://localhost:1336' + \
                ' --chrome.args="--disable-quic"' + \
                ' --chrome.args="--disable-web-security"' + \
                ' --chrome.args="--ssl-version-max=tls1.2"' + \
                ' --viewPort"'+args.viewport+'"' + \
                ' --chrome.chromedriverPath ' + chromedriver + \
                ' --chrome.collectNetLog ' + \
                extra_chromeflags + \
                ' --resultDir '+ current_batch_dir + \
                ' '+ url


            with gzip.open(current_batch_dir + '/cmdline.gz', 'w') as fd:
                 fd.write(browsertime_cmdstring)



            browsertime_process = subprocess.Popen(browsertime_cmdstring, shell=True, env=bt_env)

            print >>sys.stderr,"Running Browsertime:"
            print >>sys.stderr,browsertime_cmdstring

            def kill_timeout_cb(p, url, logfile_timeouts):

                with gzip.open(logfile_timeouts, 'w') as fd:
                     fd.write("timed out..")

                print >>sys.stderr, "Timeout Reached, will kill browsertime process..."
                p.kill()

            TIMEOUT_GLOBAL = 120*args.runs
            print "Timeout is", TIMEOUT_GLOBAL

            timer = Timer(TIMEOUT_GLOBAL, kill_timeout_cb, [
                     browsertime_process, url, current_batch_dir + '/timeout_log.gz'])

            timeout = True
            try:
                timer.start()
                browsertime_process.wait()
                timeout = False
            finally:
                # TODO(bewo): Move the entire browsertime stuff to docker to avoid resourceleaks
                proc = subprocess.Popen(["pkill", "-c" ,"-f", "tsproxy"], stdout=subprocess.PIPE)
                proc.wait()
                proc = subprocess.Popen(["pkill", "-c" ,"-f", "ffmpeg"], stdout=subprocess.PIPE)
                proc.wait()
                proc = subprocess.Popen(["pkill", "-c" ,"-f", "browsertime.js"], stdout=subprocess.PIPE)
                proc.wait()
                #proc = subprocess.Popen(["pkill", "-c" ,"-f", "chrome"], stdout=subprocess.PIPE)
                #proc.wait()
                timer.cancel()

            browsertime_success = os.path.exists(current_batch_dir+'/browsertime.json')
            browsertime_success &= os.path.exists(current_batch_dir+'/browsertime.har')

            #Compress stuff
            proc = subprocess.Popen(["gzip -f "+current_batch_dir+"/*.json"], stdout=subprocess.PIPE, shell=True)
            proc.wait()
            proc = subprocess.Popen(["gzip -f "+current_batch_dir+"/*.har"], stdout=subprocess.PIPE, shell=True)
            proc.wait()
            

            if browsertime_success is False:
                print >>sys.stderr, "WARNING: Browsertime failed!!! Attempts left: ", attempts_left
            else:
                print >>sys.stderr, "RUN COMPLETE ({} {} {})".format(url, runspec, current_batch_dir)

if __name__ == '__main__':
    main()
