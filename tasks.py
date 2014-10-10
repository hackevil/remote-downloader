#from functools import partial
from random import choice, seed

#from threading import Thread, thread
import thread
import requests
from mimetypes import guess_extension
from urlparse import urlparse
from os import getcwd, path

import traceback


class TaskManager(object):
    _instance = None
    """docstring for TaskManager"""
    @classmethod
    def getInstance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._tasks = {}

    def add(self, task):
        self._tasks[task.id] = task

        def _r(*args):
            self.remove(task.id)

        task.on('complete', _r)
        task.on('error', _r)

    def get(self, task_id):
        return self._tasks[task_id] if task_id in self._tasks else None

    def remove(self, task_id):
        if task_id in self._tasks:
            del self._tasks[task_id]


class EventEmitter(object):

    """Abstract Event Emitter"""
    REGISTERED_EVENTS = []

    def __init__(self):
        self._events = {}

    def on(self, event, listener):
        """Register an event listener on is short for addListener"""
        if event not in self.REGISTERED_EVENTS:
            raise ValueError("'{}'' is not valid event.".format(event))
        if event not in self._events:
            self._events[event] = []
        cbs = self._events[event]
        if listener not in cbs:
            cbs.append(listener)

    def emit(self, event, data):
        if event not in self.REGISTERED_EVENTS:
            raise ValueError("'{}'' is not valid event.".format(event))
        if event in self._events:
            for cb in self._events[event]:
                try:
                    cb(data)
                except Exception as e:
                    # on any error log it and go to next
                    print(e)


class Task(EventEmitter):

    """Abstract base class for all Tasks"""
    _x = seed()
    ID_CHARS = [str(x) for x in range(10)] +\
        [chr(x) for x in range(ord('a'), ord('z') + 1)] +\
        [chr(x) for x in range(ord('A'), ord('Z') + 1)]

    def __init__(self):
        super(Task, self).__init__()
        self.id = self._generate_id()

    def _generate_id(self):
        return ''.join([choice(self.ID_CHARS) for x in range(12)])


class DownloadTask(Task):
    REGISTERED_EVENTS = ['error', 'complete', 'progress']
    """Download Task"""

    def __init__(self, options):
        super(DownloadTask, self).__init__()
        self._opt = options
        # 0: not started
        # 1: running
        # 2: completed
        # 99: failed
        self.status = 0

    def run(self, app, req, ns):
        if self.status == 0:
            thread.start_new_thread(self._download_run, (app, req, ns))
            self.status = 1

    def _download_run(self, app, req, ns):
        with app.test_request_context():
            from flask import request
            from flask.ext.socketio import emit
            request = req
            request.namespace = ns
            try:
                r = requests.get(self._opt['uri'], stream=True)
                key = 'content-length'
                length = int(r.headers[key]) if key in r.headers else 0
                mime_ext = guess_extension(r.headers['content-type'])
                mime_ext = mime_ext if mime_ext else ''
                if 'saveas' in self._opt:
                    basename = self._opt['saveas']
                else:
                    basename = path.basename(urlparse(r.url).path)
                ext = ''
                name = ''
                if basename:
                    name, ext = path.splitext(basename)
                if ext == mime_ext:
                    savename = basename
                elif name:
                    savename = name + mime_ext
                else:
                    savename = self.id + mime_ext
                print(savename)
                savepath = path.join(getcwd(), 'downloads', savename)
                chunk_size = 128 * 1024
                received = 0
                with open(savepath, 'wb') as fd:
                    for chunk in r.iter_content(chunk_size):
                        received += len(chunk)
                        fd.write(chunk)
                        self.emit('progress', (received, length))
                self.emit('complete', savename)
                self.status = 2
            except Exception as ex:
                print(ex)
                traceback.print_stack()
                self.emit('error', str(ex))
                self.status = 99
