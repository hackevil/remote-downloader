from gevent import monkey
monkey.patch_all()
import time
from threading import Thread
from flask import Flask, render_template, session, request, send_file
from flask.ext.socketio import SocketIO, emit

from tasks import TaskManager, DownloadTask
from os import path, getcwd

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 's^cret!'
socketio = SocketIO(app)
thread = None


@app.route('/')
def index():
    return render_template('index.html', title="Remote Downloader")


@app.route('/download', methods=["POST"])
def download_post():
    uri = request.form['uri']
    task = DownloadTask({'uri': uri})
    TaskManager.getInstance().add(task)
    return render_template('download_progress.html', taskid=task.id)


@app.route('/downloads/<filename>', methods=["GET"])
def download_file(filename):
    """For test only, The upstream web server will provide the same function
    with position support
    """
    return send_file(path.join(getcwd(), 'downloads', filename),
                     as_attachment=True)


@socketio.on('monitor', namespace='/task')
def task_monitor(taskid):
    print("SocketIO moinitor: " + taskid)
    task = TaskManager.getInstance().get(taskid)
    if task:
        task.on('progress', lambda x: emit('progress', x))
        task.on('complete', lambda x: emit('complete', x))
        task.on('error', lambda x: emit('error', x))
        task.run(app, request, request.namespace)


@socketio.on('disconnect', namespace='/task')
def task_disconnect():
    pass


@socketio.on('connect', namespace='/task')
def task_connect():
    pass
    #print("SocketIO connected")
    #emit('my response', {'data': 'Connected', 'count': 0})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0')
