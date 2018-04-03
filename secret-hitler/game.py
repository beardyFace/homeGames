#from flask_socketio import SocketIO, emit, join_room, leave_room, \
#    close_room, rooms, disconnect

from random import randint
import random

UNASSIGNED, LIBERAL, FACIST, HITLER = 0, 1, 2 , 3

class Player():
    CITIZEN, PRESIDENT, CHANCELLOR, NOM_PRES = 0, 1, 2, 3

    def __init__(self, sid, socketio, name):
        self.sid = sid
        self.socketio = socketio
        self.name = name
        self.role = UNASSIGNED

        self.position = Player.CITIZEN
        self.last_position = self.position

    def reply(self, event, data):
        self.socketio.emit(event, data, room=self.sid, namespace='/secret-hitler')

    def gameReply(self, data):
        data['name'] = self.name
        data['role'] = self.role
        data['position'] = self.position
        self.socketio.emit('game_response', data, room=self.sid, namespace='/secret-hitler')

    def assignRole(self, role):
        self.role = role

    def assignPosition(self, assigned_position):
        self.last_position = self.position
        self.position = assigned_position

    def eligable(self, num_players):
        ineligable = (self.last_position == Player.CHANCELLOR or self.position == Player.NOM_PRES)
        if num_players > 5:
            ineligable = ineligable or self.last_position == Player.PRESIDENT
        return not ineligable

class SecretHitler():
    CMD_START = 0
    CMD_SELECT_CHANCELLOR, CMD_VOTE = 0, 1

    STATE_LOBBY, STATE_START, STATE_SLEEP, STATE_ELECT, STATE_LEGISLATIVE, STATE_EXECUTIVE, STATE_END = 0, 1, 2, 3, 4 ,5, 6
    MIN_PLAYERS      = 5
    MAX_PLAYERS      = 10
    FACIST_POLICIES  = 11
    LIBERAL_POLICIES = 6
    F_POL = 1
    L_POL = 0

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

        self.election_tracker = 0

        self.president_index = 0
        self.nom_pres   = None
        self.president  = None
        self.nom_chan   = None
        self.chancellor = None

        self.votes = {}
        self.choices = []
            
        self.polocies = self.createPolocies()
        
    def createPolocies(self):
        polocies = []
        for i in range(0, SecretHitler.FACIST_POLICIES):
            self.polocies.append(SecretHitler.F_POL)

        for i in range(0, SecretHitler.LIBERAL_POLICIES):
            self.polocies.append(SecretHitler.L_POL)
        
        random.shuffle(polocies)
        return polocies

    def getPlayerNames(self):
        names = []
        for player in self.players.values():
            names.append(player.name)
        return names

    def addPlayer(self, sid, message):
        print message
        new_player = Player(sid, self.socketio, message['name'])
        if self.state == SecretHitler.STATE_LOBBY:
            for player in self.players.values():
                if player.name == new_player.name:
                    new_player.gameReply({'state':-1, 'msg':'Name already taken!'})    
                    return

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

    def findPlayerByName(self,name):
        for player in self.players.values():
            if player.name == name:
                return player
        return None

    def processPlayerMessage(self, sid, message):
        # pass
        if self.state == SecretHitler.STATE_LOBBY:
            command = message['command']
            if command == SecretHitler.CMD_START:
                self.state = SecretHitler.STATE_START
                print('starting') 
        elif self.state == SecretHitler.STATE_ELECT:
            if 'chancellor' in message:
                self.nom_chan = self.findPlayerByName(message['chancellor'])
            if 'vote' in message:
                self.votes[sid] = message['vote']
        elif self.state == SecretHitler.STATE_LEGISLATIVE:
            if 'choice' in message:
                self.choices.append(message['choice'])

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

            elif self.state == SecretHitler.STATE_LEGISLATIVE:
                self.legislativeState()

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

        self.socketio.sleep(5)

        self.state = SecretHitler.STATE_SLEEP

    def sleepState(self):
        #send list of liberals to liberals etc
        # liberals_names = self.getRoles(LIBERAL)
        # self.messageLiberals({'state':SecretHitler.STATE_SLEEP, 'names':liberals_names})
        facists_names = self.getRoles(FACIST)
        self.messageFacists({'state':SecretHitler.STATE_SLEEP, 'names':facists_names})

        self.socketio.sleep(5)

        empty = []
        self.messagePlayers({'state':SecretHitler.STATE_SLEEP, 'names':empty})

        self.state = SecretHitler.STATE_ELECT

    def assignNominations(self):
        if self.president != None:
            self.president.assignPosition(Player.CITIZEN)
            self.president = None

        if self.chancellor != None:
            self.chancellor.assignPosition(Player.CITIZEN)
            self.chancellor = None

        self.president_index += 1
        if self.president_index == len(self.players):
            self.president_index = 0
            
        self.nom_pres = self.players[self.players.keys()[self.president_index]]
        self.nom_pres.assignPosition(Player.NOM_PRES)
        
        self.messagePlayers({'state':SecretHitler.STATE_ELECT, 'president':self.nom_pres.name})

        nominees = self.getPlayerNames()
        for player in self.players.values():
            if not player.eligable(len(self.players)):
                nominees.remove(player.name)

        self.nom_pres.gameReply({'state':SecretHitler.STATE_ELECT, 'nominees':nominees})

        self.nom_chan = None
        while self.nom_chan == None:
            self.socketio.sleep(0.1)

    def electState(self):
        self.assignNominations()

        self.messagePlayers({'state':SecretHitler.STATE_ELECT, 'nominee':self.nom_chan.name})

        self.votes = {}
        while len(self.votes) < len(self.players):
            self.socketio.sleep(0.1)

        votes_yes = 0
        votes_no  = 0
        results = []
        for player_id, vote in self.votes.iteritems():
            results.append([self.players[player_id].name, vote])
            if vote == 1:
                votes_yes += 1
            else:
                votes_no += 1
        
        self.messagePlayers({'state':SecretHitler.STATE_ELECT, 'results':results})
        self.socketio.sleep(5)

        if votes_yes > votes_no:
            #voted in
            self.chancellor = self.nom_chan
            self.president = self.nom_pres
            
            self.chancellor.assignPosition(Player.CHANCELLOR)
            self.president.assignPosition(Player.PRESIDENT)
            
            if self.fac_pol_en > 2:
                if self.chancellor.role == HITLER:
                    self.messagePlayers({'state':SecretHitler.STATE_END,'winners':FACIST})
                    self.state = SecretHitler.STATE_END
            else:
                self.state = SecretHitler.STATE_LEGISLATIVE
            # If three or more Fascist Policies have been enacted already:
            #     Ask if the new Chancellor is Hitler. If so, the game is over and the Fascists win. 
            #     Otherwise, other players know for sure the Chancellor is not Hitler.
            # Else 
            #   Proceed as usual to the Legislative Session.
        else:
            #Fail
            pass            

    def legislativeState(self): 
        self.messagePlayers({'state':SecretHitler.STATE_LEGISLATIVE,'president':self.president.name})

        if len(self.polocies) < 3:
            self.polocies = self.createPolocies()

        polocies = self.polocies[0:3]
        self.polocies = self.polocies[3:]
        self.president.gameReply({'state':SecretHitler.STATE_LEGISLATIVE, 'polocies':polocies})
        
        self.choices = []
        while(len(self.choices) < 2):
            self.socketio.sleep(0.1)

        self.chancellor.gameReply({'state':SecretHitler.STATE_LEGISLATIVE, 'polocies':self.choices})

        self.choices = []
        while(len(self.choices) < 1):
            self.socketio.sleep(0.1)

        policy = self.choices[0]

        if policy == SecretHitler.F_POL:
            self.fac_pol_en += 1
            if self.fac_pol_en > 5:
                self.messagePlayers({'state':SecretHitler.STATE_END,'winners':FACIST})
                self.state = SecretHitler.STATE_END

        else policy == SecretHitler.L_POL:
            self.lib_pol_en += 1
            if self.lib_pol_en > 4:
                print("Liberals win!")
                self.messagePlayers({'state':SecretHitler.STATE_END,'winners':LIBERAL})
                self.state = SecretHitler.STATE_END
            
        # self.state = SecretHitler.STATE_END

    def exectutiveState(self):
        pass 

    def endState(self):
        pass


