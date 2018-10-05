from urlparse import urlparse
from urlparse import urljoin

from dateutil.parser import parse

import errno    
import os
import json
import sys
import gzip
import copy

def getLocationAfterRedirects(bt_har):

    afterRedirects = bt_har['log']['entries'][0]['request']['url']

    #print "AfterRedirects1: ",afterRedirects
    
    for entry in bt_har['log']['entries']:
        redirect = entry['response']['redirectURL'] 

        if redirect:
            afterRedirects = urljoin(afterRedirects,redirect)
        else:
            break

    #print "AfterRedirects2: ",afterRedirects
    return afterRedirects

def AsciiPrintTree(dependency_tree,streams):
    print 
    for k,streams in dependency_tree.iteritems():
        print k,':',streams
    pass



def GetH2DependencyTree(netlog_file,domain,port=443):
    with gzip.open(netlog_file) as fd:
        loaded = json.load(fd)

    # Scan for the h2 connection start event

    TYPE_HTTP2_SESSION = loaded['constants']['logEventTypes']['HTTP2_SESSION']
    TYPE_HTTP2_SESSION_INITIALIZED = loaded['constants']['logEventTypes']['HTTP2_SESSION_INITIALIZED']
    TYPE_HTTP2_SESSION_SEND_HEADERS = loaded['constants']['logEventTypes']['HTTP2_SESSION_SEND_HEADERS']
    TYPE_HTTP2_STREAM_SEND_PRIORITY = loaded['constants']['logEventTypes']['HTTP2_STREAM_SEND_PRIORITY']
    TYPE_HTTP2_SESSION_RECV_PUSH_PROMISE = loaded['constants']['logEventTypes']['HTTP2_SESSION_RECV_PUSH_PROMISE']
    TYPE_HTTP2_SESSION_RECV_HEADERS = loaded['constants']['logEventTypes']['HTTP2_SESSION_RECV_HEADERS']
    TYPE_HTTP2_SESSION_RECV_DATA = loaded['constants']['logEventTypes']['HTTP2_SESSION_RECV_DATA']
    TYPE_HTTP2_SESSION_RECV_RST_STREAM = loaded['constants']['logEventTypes']['HTTP2_SESSION_RECV_RST_STREAM']


    for event in loaded['events']:
        if event['type'] == TYPE_HTTP2_SESSION:
            if event['phase'] == 1:
                if event['params']['host'] == '{}:{}'.format(domain,port):
                    source = event['source']['id']
                    break


    current_dependency_tree = dict()
    current_dependency_tree[0] = []

    global_dependency_tree = dict()
    global_dependency_tree[0] = []

    streams = dict()
    ended_streams = set()
    streams[0] = None

    for event in loaded['events']:
        echo = False
        if event['type'] == TYPE_HTTP2_SESSION_SEND_HEADERS and event['source']['id'] == source:
            #print event
            parent_stream_id = event['params']['parent_stream_id']
            stream_id = event['params']['stream_id']
            weight = event['params']['weight']
            exclusive = event['params']['exclusive']
            headers = event['params']['headers']

            streams[stream_id] = {'weight':weight,'headers':headers}

            #Check if we have dropped to stream zero, if so add a child dependency for each presucessor
            if len(current_dependency_tree[0]) == 0:
                #Add a dependency for each previous stream
                for previous_stream in global_dependency_tree:
                    global_dependency_tree[previous_stream].append(stream_id)


            #Update Global Dependency Tree:
            if parent_stream_id not in global_dependency_tree:
                global_dependency_tree[parent_stream_id] = []
            global_dependency_tree[parent_stream_id].append(stream_id)

            if exclusive:
                #Also add dependency for children
                if stream_id not in global_dependency_tree:
                    global_dependency_tree[stream_id] = []
                for child_stream in current_dependency_tree[parent_stream_id]:
                    global_dependency_tree[stream_id].append(child_stream)
            

            if exclusive:
                backup = current_dependency_tree[parent_stream_id];
                current_dependency_tree[parent_stream_id] = [stream_id]
                current_dependency_tree[stream_id] = backup
            else:
                current_dependency_tree[parent_stream_id].append(stream_id)
            


            echo = True

        elif (event['type'] == TYPE_HTTP2_STREAM_SEND_PRIORITY) and event['source']['id'] == source:
            #TODO!
            pass
        elif (event['type'] == TYPE_HTTP2_SESSION_RECV_PUSH_PROMISE) and event['source']['id'] == source:
            #TODO!
            pass

        elif (event['type'] == TYPE_HTTP2_SESSION_RECV_HEADERS
            or event['type'] == TYPE_HTTP2_SESSION_RECV_DATA) and event['source']['id'] == source:
            #print event
            if event[u'params']['fin'] == True:
                

                stream_id = event['params']['stream_id']
                ended_streams.add(stream_id)

                #find parent stream
                parent_stream_id = None
                for k,v in current_dependency_tree.iteritems():
                    if stream_id in v:
                        parent_stream_id = k
                        break

                #reparent
                current_dependency_tree[parent_stream_id].remove(stream_id)
                for child in current_dependency_tree[stream_id]:
                    current_dependency_tree[parent_stream_id].append(child)
                del current_dependency_tree[stream_id]
                echo = True


        elif event['type'] == TYPE_HTTP2_SESSION_RECV_RST_STREAM and event['source']['id'] == source:
            #print event
            stream_id = event['params']['stream_id']
            #find parent stream
            parent_stream_id = None
            for k,v in current_dependency_tree.iteritems():
                if stream_id in v:
                    parent_stream_id = k
                    break

            #reparent
            current_dependency_tree[parent_stream_id].remove(stream_id)
            
            for child in current_dependency_tree[stream_id]:
                current_dependency_tree[parent_stream_id].append(child)
            del current_dependency_tree[stream_id]

            echo = True

        #if echo:
        #    AsciiPrintTree(current_dependency_tree,streams)
    return global_dependency_tree, streams


def ComputeSerializedPushOrder(global_dependency_tree, streams):

    global_dependency_tree_working = copy.copy(global_dependency_tree)


    stream_ids_remaining = list(sorted(set(global_dependency_tree.keys())))

    #Remove initial Stream 0 and initial Request
    stream_ids_remaining.remove(0);
    stream_ids_remaining.remove(1);


    order = [1]

    while len(stream_ids_remaining)>0:

        #find next best unlinked stream
        candidateFound = False
        next_stream = None
        
        for stream_id in stream_ids_remaining:
            referenced = False
            for parent, children in global_dependency_tree_working.iteritems():
                if parent == 0 or parent == 1:
                    continue
                if stream_id in children:
                    #Stream is referenced by some parent stream, cannot proceed with that stream
                    referenced = True
                    break
            if not referenced:
                candidateFound = True
                next_stream = stream_id
                break
        assert(next_stream != None)
        
        stream_ids_remaining.remove(next_stream)
        for parent in global_dependency_tree_working:
            if next_stream in global_dependency_tree_working[parent]:
                global_dependency_tree_working[parent].remove(next_stream)
        del global_dependency_tree_working[next_stream]

        #print global_dependency_tree_working
        #print "Next Stream is:", next_stream

        order.append(next_stream)

    #print streams
    urls = []
    for stream in order:
        urls.append(getResourceNameFromHeaders(streams[stream]['headers']))
    return urls



def getResourceNameFromHeaders(headers):
    schema = ''
    host = ''
    path = ''
    for hdr in headers:
        if hdr.startswith(':path: '):
            path = hdr[len(':path: '):]
        elif hdr.startswith(':authority: '):
            host = hdr[len(':authority: '):]
        elif hdr.startswith(':scheme: '):
            schema = hdr[len(':scheme: '):]

    return schema+'://'+host+path





class PreloadClassificationException(Exception):
    pass

def classifyResourceTypeForPreload(resource):
    pass #TODO


def generateStrategyFormat(push_host=None, push_trigger=None, push_resources=[], preload_host=None, preload_trigger=None, preload_resources=[]):
    out = {}

    if push_host:
        out['push_host'] = push_host
        out['push_trigger'] = push_trigger
        out['push_resources'] = []
        for resource in push_resources:
            out['push_resources'].append(resource['url'])

    if preload_host:

        out['hint_host'] = preload_host
        out['hint_trigger'] = preload_trigger

        out['hint_resources'] = []
        for resource in push_resources:
            out['hint_resources'].append(resource['url'])

        out['hint_mimetype'] = []
        for resource in push_resources:
            out['hint_mimetype'].append(classifyResourceTypeForPreload(resource['mime']))

    return out



def getHarInfo(bt_har):
    entries = bt_har['log']['entries'] 
    resourceinfo = []
    
    for entry in entries:
        url = entry['request']['url']
        #print entry['response']['content']['mimeType']
        resourceinfo.append({
            'url': url,
            'mime': entry['response']['content']['mimeType'],
            'compressed_size': entry['response']['bodySize'],
            'uncompressed_size': entry['response']['content']['size'],
            'status': entry['response']['status']
        })

    return resourceinfo

def getSameOriginResources(prefixfilter, entries):

    

    originResources = []
    
    for entry in entries:
        url = entry['request']['url']
        if url.startswith(prefixfilter):
            #print entry['response']['content']['mimeType']
            originResources.append({
                'url': url,
                'mime': entry['response']['content']['mimeType'],
                'compressed_size': entry['response']['bodySize'],
                'uncompressed_size': entry['response']['content']['size'],
                'status': entry['response']['status']
            })

    return originResources


def getRequestedResourcesFromHar(bt_har):

    entries = bt_har['log']['entries']

    after_redirects = getLocationAfterRedirects(bt_har)

    o = urlparse(after_redirects)
    
    netloc = o.netloc
    schema = 'https://'
    
    #print after_redirects
    same_origin = getSameOriginResources(schema+netloc,entries)
    #print 'SAME ORIGIN:', getSameOriginResources(after_redirects,bt_har)

    return after_redirects, same_origin


def getH2DependencyFromNetlog(netlog, bt_har):
    
    entries = bt_har['log']['entries']
    after_redirects = getLocationAfterRedirects(bt_har)
    o = urlparse(after_redirects)

    netloc = o.netloc
    schema = 'https://'
    entries = bt_har['log']['entries'] 
    same_origin = getSameOriginResources(schema+netloc,entries)

    global_dependency_tree, streams = GetH2DependencyTree(netlog,netloc)
    h2_order_urls = ComputeSerializedPushOrder(global_dependency_tree,streams)

    originResources = []

    for h2_url in h2_order_urls:
        #search same origin entry:
        found = None
        for from_har in same_origin:
            if h2_url == from_har['url']:
                found = from_har
                break

        if found != None:
            originResources.append(found)

    return after_redirects, originResources







def filterPushableResources(after_redirects, resources):

    cleaned = []

    behindRedirect = False

    for entry in resources:
        if entry['url'] == after_redirects:
            behindRedirect = True
        else:
            if behindRedirect == True and entry not in cleaned:
                cleaned.append(entry)

    return cleaned