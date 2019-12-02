from __future__ import absolute_import
from django.conf import settings
from django.test.client import Client
from django.contrib.auth.models import User

import datetime
import time
import json
from abc import ABCMeta, abstractmethod
import six.moves.urllib.parse
import threading
from six.moves.BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from six.moves.socketserver import ThreadingMixIn, ForkingMixIn

import logging
import six
from six.moves import range
logger = logging.getLogger(__name__)

# add
import os
import string
import random
import requests
import re
from grader.models import Submission
from django.utils import timezone

# Suppress low-level network messages
logging.getLogger('requests').setLevel(logging.WARNING)


class GraderStubBase(six.with_metaclass(ABCMeta, object)):
    """Abstract base class for external grader service stubs.

    We make this abstract to accommodate the two kinds of grading servers:

    * Active: Uses the REST-like interface for pulling
        and pushing requests to the XQueue.


    * Passive: Waits for XQueue to send it a message,
        then responds synchronously."""

    @staticmethod
    def build_response(submission_id, submission_key, score_msg):
        """Construct a valid xqueue response

        `submission_id`: Graded submission's database ID in xqueue (int)
        `submission_key`: Secret key to match against XQueue database (string)
        `score_msg`: Grading result from external grader (string)

        Returns: valid xqueue response (dict)"""
        return json.dumps({'xqueue_header':
                           {'submission_id': submission_id,
                            'submission_key': submission_key},
                           'xqueue_body': score_msg})
    @abstractmethod
    def submit(self, real_pid, source):
        pass

    @abstractmethod
    def response_for_submission(self, submission):
        """Respond to an XQueue submission.

        Subclasses implement this method, usually to either:

        * Return a pre-defined response from `build_response(`)

        * Forward the call to the actual external grader,
            then return the result.

        * Return an invalid response to test error handling.

        `submission`: dict of the form
            {'xqueue_header': {'submission_id': ID,
                                'submission_key': KEY },
            'xqueue_body: STRING,
            'xqueue_files': list of file URLs }

        returns: dictionary

        XQueue expects the dict to be of the form used by
        `build_response()`, but you can provide invalid responses
        to test error handling."""
        pass

    
class ActiveGraderStub(GraderStubBase):
    """Stub for an active grader, which polls the XQueue for new
    submissions, processes the submissions, then pushes
    responses back to the XQueue.  It uses XQueue's REST-like interface.

    It runs a daemon thread to asynchronously poll the XQueue."""

    SLEEP_TIME = 0.5

    USERNAME = 'lms'
    PASSWORD = 'password'

    _poll_thread = None
    _is_polling = True
    _queue_name = None

    def __init__(self, queue_name):
        """Start polling the Xqueue for new submissions"""

        # Store the queue name, so we know
        # which queue to poll
        self._queue_name = queue_name

        # login connection
        self._client = XQueueClient("http://34.92.186.97:8080", self.PASSWORD)
        self._client.login()

        # The polling thread will run until
        # this flag is set to False
        self._is_polling = True

        self.poll()
        
        # Start polling the XQueue
        # self._poll_thread = threading.Thread(target=self.poll)
        # self._poll_thread.daemon = True
        # self._poll_thread.start()

    def stop(self):
        """Stop polling the XQueue"""
        self._is_polling = False

    def poll(self):
        """Poll the XQueue for new submissions, delegating
        to concrete subclasses to determine the response."""

        # Check the running flag
        while self._is_polling:

            # Try to get a submission
            submission = self._pop_submission()

            # If we can't get one now, wait a bit then retry
            if submission is None:
                time.sleep(ActiveGraderStub.SLEEP_TIME)

            # Otherwise, process the submission
            # and push a response back to the XQueue
            else:

                # Delegate to the concrete base class
                # to create a response
                response = self.response_for_submission(submission)

                # Push the response back to the XQueue
                self._push_response(response)

    def _pop_submission(self):
        """Attempts to pop a submission from the XQueue.
        If it succeeds, it returns a `dict` of the submission info,
        which has keys `xqueue_header` and `xqueue_body`
        (and sometimes `xqueue_files` as well).

        The `xqueue_header` is itself a JSON-decoded dict,
        but `xqueue_body` is a string.

        If no submission is available, or an error occurs,
        returns None."""

        # Use the Django test client to retrieve a submission
        # from our queue
        response = self._client.get_request('/xqueue/get_submission/?queue_name='+self._queue_name) # get

        # If any kind of HTTP error occurred,
        # log it and return None
        if response.status_code != 200:
            logger.warning('Could not get submission from XQueue: status = %d',
                           response.status_code)
            return None

        # Otherwise the response was successful
        else:

            # JSON-decode the response
            response_dict = json.loads(response.content)

            # Check that we successfully retrieved a submission
            if response_dict['return_code'] == 0:

                # If so, JSON-decode the submission and
                # return the resulting dict
                submission_dict = json.loads(response_dict['content'])
                xqueue_header = json.loads(submission_dict['xqueue_header'])
                xqueue_body = submission_dict['xqueue_body']
                return {'xqueue_header': xqueue_header,
                        'xqueue_body': xqueue_body}

            # Otherwise, we could not retrieve the submission,
            # usually because the queue is empty.
            else:
                return None
            
    # Override
    def response_for_submission(self, submission):
        print(submission)
        # Construct the response
        xqueue_header = submission['xqueue_header']
        xqueue_body = submission['xqueue_body']
        
        raw = json.loads(submission['xqueue_body'])
        r_pid = raw['grader_payload']
        
        war = json.loads(r_pid)
        pid = war['problem_name']

        r_who = raw['student_info']
        h_dict = json.loads(r_who)
        who = h_dict['anonymous_student_id']
        
        source = raw['student_response']
        
        xqueue_body = self.submit(pid, source)

        if xqueue_body['correct']:
            status = 'Accepted'
        else:
            status = 'W/a'

        submission_id = submission['xqueue_header']['submission_id']
        fname = "problem_" + pid + '/' + str(submission_id) + ".txt"

        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        try:
            with open(os.path.join(BASE_DIR + "/media/", fname), "w") as f:
                f.write(source)
        except OSError as e:
            print(e)

        q = Submission(pid=pid, submission_id=submission_id,
                       source=fname,
                       who=who,
                       when=timezone.now(),
                       status=status)
        q.save()
        return {'xqueue_header': xqueue_header,
                'xqueue_body': xqueue_body}

    def submit(self, pid, source):
        """Run code in Isolate"""
        # анхны pid -г хадгалч авах
        real_pid = pid

        # pid -нд санамсаргүй угтвар залгах
        letters = string.ascii_lowercase
        pid += ''.join(random.choice(letters) for i in range(5))
        
        # С код болгох
        out = pid + ".c"
        fw = open(out, "w")
        fw.write(source)
        fw.close()
        
        # compile хийж программаа гаргах (exe файл үүсгэх)
        res = pid + "output"
        com = "gcc " + out + " -o " + pid + " 2> " + res
        r = os.system(com)

        # source алдаатай эсэхийг шалгах
        fr = open(res, "r") 
        compile_error = fr.read()
        fr.close()

        if (compile_error):
            rm = "rm -rf " + pid + " " + out + " " + res
            os.system(rm)
            correct = False
            score = 0
            return {'correct': correct,
                    'score': score,
                    'msg': compile_error}

        # программ isolate дотор ажиллуулах
        cp = "sudo cp -rf " + pid + " /var/local/lib/isolate/0/box/"
        os.system(cp)
        
        # running program in isolate
        # sand = "./sol.sh" + " problem_" + real_pid + " " + pid + " > " + res
        sand = "./media/./sol.sh" + " ./media/problem_" + real_pid + " " + pid + " > " + res
        os.system(sand)

        # pass counter
        fr = open(res, "r") 
        ret = fr.read()
        fr.close()

        # бүх үүсгэсэн файл, програмуудыг устгах
        rm = "rm -rf " + pid + " " + out + " " + res
        os.system(rm)

        correct = True
        ret_dict = json.loads(ret)
        for i in ret_dict : 
            a = i

        b = ret_dict[str(a)]
        
        try:
            score = int(a) / int(b)
        except ZeroDivisionError:
            score = 0
            
        if score == 1:
            correct = True
        else:
            correct = False
        print(score)
        
        msg = str(a) + "/" + str(b)

        
        print(msg)
        return {'correct': correct,
                'score': score,
                'msg': msg}

    def _push_response(self, response_dict):
        """Push a response back to the XQueue.
        `response_dict` is a JSON-serializable dictionary
        with keys `xqueue_header` and `xqueue_body`,
        both JSON-serialized strings.

        Returns `True` if successful, `False` otherwise."""

        # Construct the response
        xqueue_header = response_dict['xqueue_header']
        xqueue_body = response_dict['xqueue_body']

        post_params = {'xqueue_header': json.dumps(xqueue_header),
                       'xqueue_body':   json.dumps(xqueue_body)}
        
        #params = json.dumps(post_params)
        print(post_params)
        print(type(post_params))

        # Use the Django test client to POST a response
        # back to the XQueue
        response = self._client.send_request('/xqueue/put_result/', post_params) # send
        # response = self._client.send_request('/xqueue/submit/', params)       # send
        
        # Check the status code, and log a warning if we failed
        if response.status_code != 200:
            logger.warning('Could not push response to XQueue: status=%d',
                           response.status_code)
            return False

        else:
            # Check the response's return_code and log a warning if we failed
            response_dict = json.loads(response.content)
            if response_dict['return_code'] != 0:
                logger.warning('Could not submit response to XQueue: %s',
                               response_dict['content'])
                return False

            # Otherwise, everything was successful
            else:
                return True
            

class XQueueClient(object):
    """
    Test client to simulate a hello world problem
    submission
    """
    # XQueueClient('http://34.92.186.97:8080', 'password', 'url')
    # http://localhost:8040
    def __init__(self, server, passwd):
        self.s = requests.session()
        self.server = server
        self.passwd = passwd

    def login(self):
        logger.info("logging in...")
        r = self.s.post(self.server + '/xqueue/login/',
                        {'username': 'lms', 'password': self.passwd})
        r.raise_for_status()
        logger.debug("login response: %r", r.json)

    def send_request(self, url, param):
        """Send a request to the xqueue."""
        response = self.s.post(self.server + url, param)
        return response

    def get_request(self, url):
        response = self.s.get(self.server + url)
        return response
