#from flask_socketio import SocketIO, emit, join_room, leave_room, \
#    close_room, rooms, disconnect

from random import randint

UNASSIGNED, LIBERAL, FACIST, HITLER = 'Unassigned', 'Liberal', 'Facist' , 'Hitler'

class Player():
    def __init__(self, sid, socketio, name):
    	self.sid = sid
        self.socketio = socketio
        
        self.name = name
        self.role = UNASSIGNED

    def reply(self, event, data):
        self.socketio.emit(event, data, room=self.sid, namespace='/test')

    def assignRole(self, role):
    	self.role = role

class SecretHitler():
	STATE_START, STATE_SLEEP, STATE_VOTE, STATE_ELECT, STATE_LEGISLATIVE, STATE_EXECUTIVE = 0, 1, 2, 3, 4 ,5
	MIN_PLAYERS      = 5
	MAX_PLAYERS      = 10
	FACIST_POLICIES  = 11
	LIBERAL_POLICIES = 6

	def __init__(self, socketio):
		self.socketio = socketio

		self.players = {}
		self.state = SecretHitler.STATE_START

		self.facists  = []
		self.liberals = []
		self.hitler   = None

		self.fac_pol_en  = 0
		self.lib_pol_en = 0

		self.president  = None
		self.chancellor = None

		#5 -6 six players
		#Close your eyes
		#F and H open eyes and acknowledge each other
		#Close eyes
		#Everyone open eyes

		#7 - 10
		#F know H but H not know F

		#Rounds
		#Election

		#Legislative

		#Executive action



	def addPlayer(self, sid, message):
		if self.state == STATE_START:
			new_player = Player(sid, self.socketio, message['name'])
			for player in self.players.values():
				player.reply('my_response', {'data': 'Player '+new_player.name+' connected', 'count': 0})
			self.players[sid] = new_player

	def removePlayer(self, sid):
		name = self.players[sid].name
		del self.players[sid]
		for player in self.players.values():
			player.reply('my_response', {'data': 'Player '+name+' disconnected', 'count': 0})

	def processPlayerMessage(self, sid, message):
		# command = message['command']
		# if command == ADD_NAME:
		# 	player[sid].addName(message['data'])
		self.players[sid].reply('my_response', {'data': message['data'], 'count': 0})


	def run(self):
		count = 0
		end_game = False
		while end_game != True:
			self.socketio.sleep(0.1)
			if self.state == SecretHitler.STATE_START:
				self.startState()
			elif self.state == SecretHitler.STATE_DAY:
				self.dayState()
			elif self.state == SecretHitler.STATE_NIGHT:
				self.nightState()
			elif self.state == SecretHitler.STATE_END:
				self.endState()
				end_game = True

	def startState(self):
		ready = len(self.players) > 3
		self.socketio.sleep(0.1)
		if ready:
			for player in self.players.values():
				player.reply('my_response', {'data': 'Ready to start!', 'count': 0})
		# self.state = SecretHitler.STATE_DAY

	def dayState(self):
		print("DAY")

	def nightState(self):
		print("NIGHT")

	def endState(self):
		pass


