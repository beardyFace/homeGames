#from flask_socketio import SocketIO, emit, join_room, leave_room, \
#    close_room, rooms, disconnect

from random import randint
import random

UNASSIGNED, LIBERAL, FACIST, HITLER = 0, 1, 2 , 3

class Player():
    def __init__(self, sid, socketio, name):
        self.sid = sid
        self.socketio = socketio
        self.name = name
        self.role = UNASSIGNED

        self.eligable = True

    def reply(self, event, data):
        self.socketio.emit(event, data, room=self.sid, namespace='/secret-hitler')

    def gameReply(self, data):
        data['name'] = self.name
        data['role'] = self.role
        self.socketio.emit('game_response', data, room=self.sid, namespace='/secret-hitler')

    def assignRole(self, role):
        self.role = role

class SecretHitler():
    CMD_START = 0

    STATE_LOBBY, STATE_START, STATE_SLEEP, STATE_ELECT, STATE_LEGISLATIVE, STATE_EXECUTIVE, STATE_END = 0, 1, 2, 3, 4 ,5, 6
    MIN_PLAYERS      = 5
    MAX_PLAYERS      = 10
    FACIST_POLICIES  = 11
    LIBERAL_POLICIES = 6

    def __init__(self, socketio):
        self.socketio = socketio
        self.players = {}
        self.state = SecretHitler.STATE_LOBBY

        self.num_facists = 0
        self.facists  = []

        self.num_liberals = 0
        self.liberals = []
        self.hitler   = None

        self.fac_pol_en  = 0
        self.lib_pol_en = 0

        self.president_index = 0
        self.president  = None
        self.chancellor = None

        self.votes = {}

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

    def getPlayerNames(self):
        names = []
        for player in self.players.values():
            names.append(player.name)
        return names

    def addPlayer(self, sid, message):
        print message
        new_player = Player(sid, self.socketio, message['name'])
        if self.state == SecretHitler.STATE_LOBBY:
            self.players[sid] = new_player
            
            names = self.getPlayerNames()
            for player in self.players.values():
                player.gameReply({'state':SecretHitler.STATE_LOBBY, 'names': names, 'ready':0})
        else:
            new_player.gameReply({'state':SecretHitler.STATE_LOBBY, 'message': 'Game has already started sorry!!'})

    def removePlayer(self, sid):
        if sid in self.players:
            del self.players[sid]
            if self.state == SecretHitler.STATE_LOBBY:
                names = self.getPlayerNames()
                for player in self.players.values():
                    player.gameReply({'state':SecretHitler.STATE_LOBBY, 'names': names, 'ready':0})

    def processPlayerMessage(self, sid, message):
        # pass
        if self.state == SecretHitler.STATE_LOBBY:
            command = message['command']
            if command == SecretHitler.CMD_START:
                self.state = SecretHitler.STATE_START
                print('starting')        

    def messagePlayers(self, message):
        for player in self.players.values():
            player.gameReply(message)

    def messageLiberals(self, message):
        for libearl_id in self.liberals:
            self.players[libearl_id].gameReply(message)

    def messageFacists(self, message, msg_hitler=True):
        for facist_id in self.facists:
            self.players[facist_id].gameReply(message)
        if msg_hitler:
            self.players[self.hitler].gameReply(message)

    def getRoles(self, role):
        names = []
        for player in self.players.values():
            if player.role == role:
                names.append(player.name)
        return names

    def run(self):
        self.lobbyState()

        end_game = False
        while end_game != True:
            self.socketio.sleep(0.1)
            if self.state == SecretHitler.STATE_START:
                self.startState()
            
            elif self.state == SecretHitler.STATE_SLEEP:
                self.sleepState()

            elif self.state == SecretHitler.STATE_ELECT:
                self.electState()

            elif self.state == SecretHitler.STATE_END:
                self.endState()
                end_game = True

    def lobbyState(self):
        sent_ready_msg = False
        while self.state == SecretHitler.STATE_LOBBY:
            ready = len(self.players) > SecretHitler.MIN_PLAYERS
            self.socketio.sleep(0.1)
            names = self.getPlayerNames()

            message = {'state':SecretHitler.STATE_LOBBY, 'names':names, 'ready':(1 if ready else 0)};
            if ready and not sent_ready_msg:
                self.messagePlayers(message)
                sent_ready_msg = True
            elif not ready and sent_ready_msg:
                self.messagePlayers(message)
                sent_ready_msg = False


    def startState(self):
        num_players = len(self.players)
        if num_players == 5:
            self.num_liberals = 3
            self.num_facists = 1
        if num_players == 6:
            self.num_liberals = 4
            self.num_facists = 1
        if num_players == 7:
            self.num_liberals = 4
            self.num_facists = 2
        if num_players == 8:
            self.num_liberals = 5
            self.num_facists = 2
        if num_players == 9:
            self.num_liberals = 5
            self.num_facists = 3
        if num_players == 10:
            self.num_liberals = 6
            self.num_facists = 3

        keys = self.players.keys()

        #Assign hitler and the facists
        self.hitler = random.choice(keys)
        keys.remove(self.hitler)
        self.players[self.hitler].assignRole(HITLER)
        
        for i in range(0, self.num_facists):
            facist = random.choice(keys) 
            keys.remove(facist)
            self.facists.append(facist)
            self.players[facist].assignRole(FACIST)

        #Assign liberals
        for key in keys:
            self.liberals.append(key)
            self.players[key].assignRole(LIBERAL)

        msg = {'state':SecretHitler.STATE_START}
        #notify everyone of their role
        self.messagePlayers(msg)

        self.socketio.sleep(10)

        self.state = SecretHitler.STATE_SLEEP

    def sleepState(self):
        #send list of liberals to liberals etc
        # liberals_names = self.getRoles(LIBERAL)
        # self.messageLiberals({'state':SecretHitler.STATE_SLEEP, 'names':liberals_names})
        facists_names = self.getRoles(FACIST)
        self.messageFacists({'state':SecretHitler.STATE_SLEEP, 'names':facists_names})

        self.socketio.sleep(10)

        empty = []
        self.messagePlayers({'state':SecretHitler.STATE_SLEEP, 'names':empty})

        self.state = SecretHitler.STATE_ELECT

    def electState(self):

        if self.president == None:
            self.president = random.choice(self.players.keys())
            for index, player_key in enumerate(self.players.keys()):
                if self.president == player_key:
                    self.president_index = index
                    break
        else:
            self.president_index += 1
            if self.president_index == len(self.players):
                self.president_index = 0
            self.president = self.players.keys()[self.president_index]

        self.players[self.president].reply('game_response', {'data':'You are the president'})

        self.socketio.sleep(5)

        self.players[self.president].reply('game_response', {'data':'Select a chancellor'})

        self.chancellor = None
        while self.chancellor == None:
            self.socketio.sleep(0.1)

        nominee = self.players[self.chancellor]
        self.players[self.chancellor].reply('my_response', {'data': nominee.name+' has been nominated for chancellor'})

        self.messagePlayers({'data':'Vote for '+nominee.name+' to be chancellor'})

        self.votes = {}
        while len(self.votes) < len(self.players):
            self.socketio.sleep(0.1)

        votes_yes = 0
        votes_no  = 0
        msg = ''
        for player_id, vote in self.votes.iteritems():
            msg += self.players[player_id].name + " voted: " + vote +"\n"
            if vote == 'yes':
                votes_yes += 1
            else:
                votes_no += 1

        self.messagePlayers({'data': msg})

        if votes_yes > votes_no:
            #voted in
            pass
        elif votes_yes == votes_no:
            #tie
            pass
        else:
            #fail
            pass            

    def legislativeState(self): 
        pass

    def exectutiveState(self):
        pass 

    def endState(self):
        pass


