#!/usr/bin/env python2.7
"""
TestAPI program
"""
from __future__ import print_function
import os
import time
import json
import sys
import pprint
from datetime import datetime
import falcon

class ReturnCodeResource(object):
    """Return Service"""
    @staticmethod
    def log(msg):
        """Writes Log"""
        print("[%s] [DEBUG] %s" % (datetime.now(), msg))

    @staticmethod
    def err(msg):
        """Writes Error"""
        print("[%s] [ERROR] %s" % (datetime.now(), msg))

    def on_post(self, req, resp):
        """Listen POST and set ENV Variable 'RESULT'"""
        body = req.stream.read()
        param = json.loads(body)
        got = param['RESULT'].encode('utf-8', 'replace')
        self.log("Setting env var to " + got)
        os.environ['RESULT'] = got
        resp.status = falcon.HTTP_200
        resp.body = 'RESULT env var changed to: ' + got

    def on_get(self, req, resp):
        """Listen GET and Return specific CODE"""
        self.log("Return Code received.")
        option = os.getenv('RESULT', '')

        # Response
        if option == 'N':
            self.log("Not healthy - Simulated")
            resp.status = falcon.HTTP_404
            resp.body = 'Not healthy'
        elif option == 'T':
            self.log("Time Out - Simulated (35 seg of delay)")
            time_delay = int(API_TIME_DELAY)
            time.sleep(time_delay)
            resp.status = falcon.HTTP_200
            resp.body = '200'
        else:
            self.log("200")
            resp.status = falcon.HTTP_200
            resp.body = '200'

class PingResource(object):
    """Ping Service"""
    def on_get(self, req, resp):
        """Listen GET for PING"""
        resp.status = falcon.HTTP_200
        resp.body = 'PONG'

class RootResource(object):
    """Root Service"""
    def on_get(self, req, resp):
        """Handles GET requests"""
        app_envvars = {k: v for k, v in os.environ.iteritems() if k.startswith('APP')}
        envs = ''
        for k, val in app_envvars.iteritems():
            envs += '{} = {}\n        '.format(k, val)
        resp.status = falcon.HTTP_200
        resp.body = 'Welcome to {name}\n\n\
        Get Help => GET /help\n\n\
        Environment Variables (APP*):\n\
        {envs}'.format(name=API_NAME, envs=envs.strip())

class CounterResource(object):
    """Handles request to increment on each one"""
    def __init__(self):
        self.count = 0

    def on_get(self, req, resp):
        self.count = self.count + 1
        resp.status = falcon.HTTP_200
        resp.body = str(self.count)

class JsonResource(object):
    """Handles all Json request"""
    def on_get(self, req, resp):
        """Handles GET requests"""
        quote = {
            'quote': 'I\'ve always been more interested in the future than in the past.',
            'author': 'Grace Hopper'
        }
        resp.status = falcon.HTTP_200
        resp.body = json.dumps(quote)

class HelpResource(object):
    """Shows help to the user"""
    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200
        resp.body = '\
        App Name: Environment MARATHON_APP_ID or APP_ID\n\
        GET /ping  => Return PONG string\n\
        GET /json  => Return JSON object\n\
        GET /count => Return incremental number\n\
        POST /stdout => Write to STDOUT (parameter "err=1" to STDERR):\n\
                        text: YOUR MESSAGE\n\
                        json: {"msg": "YOUR MESSAGE"}\n\
        POST /rest   => Logs to STDOUT the posted data\n\
        POST /doc    => Save the POSTED text data as plain text (Default )\n\
         GET /doc    => Get all document\n\
         GET /doc/#  => Returns ONLY the line (without \\n) from the text posted.\n\
         GET /return => Return specific response code (default 202)\n\
        POST /return => To change the response to Error 404 > text: RESULT=N\n\
                        To change to Timeout (set in API_TIMEOUT_DELAY)> text: RESULT=T\n'

class StdoutResource(object):
    """Handles STDOUT and STDERR raw output"""
    def on_post(self, req, resp):
        body = req.stream.read()
        is_error = req.get_param_as_bool('err', required=False, store=None, blank_as_true=False)
        ReturnCodeResource.log("Query Params: " + str(req.params))
        ReturnCodeResource.log("content-type: " + req.content_type)
        if req.content_type == 'application/json':
            try:
                obj = json.loads(body)
                if 'msg' in obj:
                    msg = obj['msg']
                else:
                    ReturnCodeResource.log("No 'msg' property given.")
                    msg = body
            except ValueError as e:
                ReturnCodeResource.log(e.message)
                msg = body
        else:
            msg = body
        resp.status = falcon.HTTP_200

        if is_error:
            resp.body = 'Writen to STDERR:\n{}'.format(msg)
            print_error(msg)
        else:
            resp.body = 'Writen to STDOUT:\n{}'.format(msg)
            print(msg)

class DocumentResource(object):
    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200
        resp.body = DOCUMENT_TEXT

    def on_post(self, req, resp):
        body = req.stream.read()
        global DOCUMENT_TEXT
        DOCUMENT_TEXT = body
        resp.status = falcon.HTTP_200
        resp.body = 'Saved the document:\n' + body

class DocumentLineResource(object):
    def __init__(self):
        self.text = ''

    def on_get(self, req, resp, line):
        if line < 1:
            resp.status = falcon.HTTP_406
            resp.body = '# The line number must be greater than 0'.format(line)
            return

        lines = DOCUMENT_TEXT.splitlines()

        correct_line = line - 1
        num_lines = len(lines)
        ReturnCodeResource.log('Getting line #{} of a total {}'.format(line, num_lines))

        if line <= num_lines:
            string_in_line = lines[correct_line]
            resp.status = falcon.HTTP_200
            resp.body = string_in_line
        else:
            ReturnCodeResource.err('Got line num {}, when there are only {}'.format(line, len(lines)))
            resp.status = falcon.HTTP_406
            resp.body = '# The line number {} does not exists'.format(line)

class RestResource(object):
    def on_post(self, req, resp):
        for num, line in enumerate(req.headers):
            ReturnCodeResource.log('Header {} --> {}: {}'.format(num, line, req.headers[line]))

        body = req.stream.read()
        ReturnCodeResource.log('Data got:\n' + body)
        resp.status = falcon.HTTP_200
        resp.body = 'AWK\n'

def print_error(*args, **kwargs):
    """Prints arguments to STDERR"""
    print(*args, file=sys.stderr, **kwargs)

MARATHON_ID = os.getenv('MARATHON_APP_ID', 'TestAPI')
APP_ID = os.getenv('APP_ID', '')
API_NAME = APP_ID if APP_ID != '' else MARATHON_ID
API_TIME_DELAY = os.getenv('API_TIMEOUT_DELAY', '35')
DOCUMENT_TEXT = '1\n2\n3\n4\n5\n6\n7\n8\n9\n10'

APP = falcon.API()
APP.req_options.keep_blank_qs_values = True

APP.add_route('/', RootResource())
APP.add_route('/ping', PingResource())
APP.add_route('/return', ReturnCodeResource())
APP.add_route('/count', CounterResource())
APP.add_route('/json', JsonResource())
APP.add_route('/help', HelpResource())
APP.add_route('/stdout', StdoutResource())
APP.add_route('/rest', RestResource())
APP.add_route('/doc', DocumentResource())
APP.add_route('/doc/{line:int}', DocumentLineResource())

ReturnCodeResource.log("Started")
