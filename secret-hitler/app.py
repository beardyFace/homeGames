#!/usr/bin/env python
# import eventlet
# eventlet.monkey_patch()
from threading import Lock
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
from game import SecretHitler

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

app = Flask(__name__, template_folder='./build', static_folder='./build/static')
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()

game = SecretHitler(socketio)

def background_thread():
    game.run()        

@app.route('/')
def index():
    # return render_template('index.html', async_mode=socketio.async_mode)
    return render_template('index.html', async_mode=socketio.async_mode)

@socketio.on('join', namespace='/secret-hitler')
def joinMessage(message):
    game.addPlayer(request.sid, message)

@socketio.on('player_response', namespace='/secret-hitler')
def joinMessage(message):
    game.processPlayerMessage(request.sid, message)

@socketio.on('connect', namespace='/secret-hitler')
def test_connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=background_thread)

    print 'connection established'
    
    # emit('game_response', {'state':0}, namespace='/secret-hitler')

@socketio.on('disconnect', namespace='/secret-hitler')
def test_disconnect():
    # del clients[request.sid]
    game.removePlayer(request.sid)
    print('Client disconnected', request.sid)

if __name__ == '__main__':
    socketio.run(app, debug=True)