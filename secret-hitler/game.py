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
        print("------------------------")
        print(self.name)
        print(self.last_position)
        print(self.position)
        ineligable = (self.last_position == Player.CHANCELLOR or self.position == Player.NOM_PRES)
        if num_players > 5:
            ineligable = ineligable or self.last_position == Player.PRESIDENT
        return not ineligable

class SecretHitler():
    CMD_START = 0
    CMD_SELECT_CHANCELLOR, CMD_VOTE = 0, 1

    STATE_LOBBY, STATE_START, STATE_SLEEP, STATE_ELECT, STATE_LEGISLATIVE, STATE_EXECUTIVE, STATE_END = 0, 1, 2, 3, 4 ,5, 6
    EXEC_NONE, EXEC_INV, EXEC_ELE, EXEC_PEEK, EXEC_KILL, EXEC_VETO = 0, 1, 2, 3, 4, 5

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

        self.nom_player = None

        self.votes = {}
        self.choices = []
            
        self.exectuve_actions = None
        self.polocies = self.createPolocies()
        
    def createExecutiveActions(self, num_players):
        exectuve_actions = []
        if num_players < 7:
            exectuve_actions.append(SecretHitler.EXEC_NONE)
            exectuve_actions.append(SecretHitler.EXEC_NONE)
            exectuve_actions.append(SecretHitler.EXEC_PEEK)
        elif num_players < 9:
            exectuve_actions.append(SecretHitler.EXEC_NONE)
            exectuve_actions.append(SecretHitler.EXEC_INV) 
            exectuve_actions.append(SecretHitler.EXEC_ELE)
        else:
            exectuve_actions.append(SecretHitler.EXEC_INV)
            exectuve_actions.append(SecretHitler.EXEC_INV) 
            exectuve_actions.append(SecretHitler.EXEC_ELE)

        exectuve_actions.append(SecretHitler.EXEC_KILL)
        exectuve_actions.append(SecretHitler.EXEC_KILL)

        return exectuve_actions

    def createPolocies(self):
        polocies = []
        for _ in range(0, SecretHitler.FACIST_POLICIES):
            polocies.append(SecretHitler.F_POL)

        for _ in range(0, SecretHitler.LIBERAL_POLICIES):
            polocies.append(SecretHitler.L_POL)
        
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
        print(message)
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
        elif self.state == SecretHitler.STATE_EXECUTIVE:
            if 'player' in message:
                self.nom_player = self.findPlayerByName(message['player'])

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

    def getPolocies(self, number):
        policies = self.polocies[:number]
        self.polocies = self.polocies[number:]
        
        if len(self.polocies) < 3:
            self.polocies = self.createPolocies()

        return policies

    def run(self):
        self.lobbyState()
        self.startState()
        self.sleepState()

        end_game = False
        while end_game != True:
            if self.electState():
                self.endState()
                end_game = True

    def lobbyState(self):
        print("Lobby")
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
        print("Start")
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

        self.exectuve_actions = self.createExecutiveActions(num_players)

        action = self.exectuve_actions[self.fac_pol_en]
        print(action)
        
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
        print("Sleep")
        #send list of liberals to liberals etc
        # liberals_names = self.getRoles(LIBERAL)
        # self.messageLiberals({'state':SecretHitler.STATE_SLEEP, 'names':liberals_names})
        facists_names = self.getRoles(FACIST)
        self.messageFacists({'state':SecretHitler.STATE_SLEEP, 'names':facists_names})

        self.socketio.sleep(5)

        empty = []
        self.messagePlayers({'state':SecretHitler.STATE_SLEEP, 'names':empty})

    def assignNextPresident(self, next_president):
        if self.president != None:
            self.president = None

        if next_president == None:
            self.president_index += 1
            if self.president_index == len(self.players):
                self.president_index = 0
                
            self.nom_pres = self.players[self.players.keys()[self.president_index]]
        else:
            self.nom_pres = next_president
            
        self.nom_pres.assignPosition(Player.NOM_PRES)
        
        self.messagePlayers({'state':SecretHitler.STATE_ELECT, 'president':self.nom_pres.name})

    def nominateChancellor(self):
        if self.chancellor != None:
            self.chancellor = None

        nominees = self.getPlayerNames()
        for player in self.players.values():
            if not player.eligable(len(self.players)):
                nominees.remove(player.name)

        self.nom_pres.gameReply({'state':SecretHitler.STATE_ELECT, 'nominees':nominees})

        self.nom_chan = None
        while self.nom_chan == None:
            self.socketio.sleep(0.1)

    def electState(self, next_president=None):
        print("Elect")
        self.state = SecretHitler.STATE_ELECT
        
        for player in self.players.values():
            player.assignPosition(Player.CITIZEN)

        self.assignNextPresident(next_president)
        self.nominateChancellor()

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
            print("Vote passed")
            #voted in
            self.chancellor = self.nom_chan
            self.president = self.nom_pres
            
            self.chancellor.assignPosition(Player.CHANCELLOR)
            self.president.assignPosition(Player.PRESIDENT)
            
            if self.fac_pol_en > 2:
                if self.chancellor.role == HITLER:
                    return self.declareWinners(FACIST)
            return self.legislativeState()
        else:
            print("Vote failed")
            self.election_tracker += 1
            self.messagePlayers({'state':SecretHitler.STATE_ELECT, 'chaos':self.election_tracker})
            self.socketio.sleep(5)
            
            if self.election_tracker > 2:#chaos
                policy = self.getPolocies(0)

                self.messagePlayers({'state':SecretHitler.STATE_ELECT, 'policy':policy})
                self.socketio.sleep(5)
                
                if policy == SecretHitler.F_POL:
                    self.fac_pol_en += 1
                    if self.fac_pol_en > 5:
                        return self.declareWinners(FACIST)
                elif policy == SecretHitler.L_POL:
                    self.lib_pol_en += 1
                    if self.lib_pol_en > 4:
                        return self.declareWinners(LIBERAL)

                self.election_tracker = 0
                
        return False

    def legislativeState(self): 
        print("Legislative")
        self.state = SecretHitler.STATE_LEGISLATIVE
        
        self.messagePlayers({'state':SecretHitler.STATE_LEGISLATIVE,'president':self.president.name})

        polocies = self.getPolocies(3)
        
        self.president.gameReply({'state':SecretHitler.STATE_LEGISLATIVE, 'polocies':polocies})
        
        self.choices = []
        while(len(self.choices) < 2):
            self.socketio.sleep(0.1)

        self.chancellor.gameReply({'state':SecretHitler.STATE_LEGISLATIVE, 'polocies':self.choices})

        self.choices = []
        while(len(self.choices) < 1):
            self.socketio.sleep(0.1)

        policy = self.choices[0]
        
        if int(policy) == SecretHitler.F_POL:
            self.fac_pol_en += 1
            if self.fac_pol_en > 5:
                return self.declareWinners(FACIST)
            else:
                return self.exectutiveState()
        elif int(policy) == SecretHitler.L_POL:
            self.lib_pol_en += 1
            if self.lib_pol_en > 4:
                return self.declareWinners(LIBERAL)

        return False
                                
    def exectutiveState(self):
        print("Executive")
        self.state = SecretHitler.STATE_EXECUTIVE
        
        action = self.exectuve_actions[self.fac_pol_en-1]
        print(action)

        self.messagePlayers({'state':SecretHitler.STATE_EXECUTIVE, 'action':action})
        if action != SecretHitler.EXEC_NONE:
            if action == SecretHitler.EXEC_PEEK:
                polocies = self.polocies[:3]
                self.president.gameReply({'state':SecretHitler.STATE_EXECUTIVE, 'action':action, 'polocies':polocies})
                self.socketio.sleep(10)
            else:
                names = self.getPlayerNames()
                
                self.president.gameReply({'state':SecretHitler.STATE_EXECUTIVE, 'names':names, 'action':action})

                self.nom_player = None
                while self.nom_player == None:
                    self.socketio.sleep(0.1)

                if action == SecretHitler.EXEC_INV:
                    role = self.nom_player.role
                    name = self.nom_player.name
                    self.president.gameReply({'state':SecretHitler.STATE_EXECUTIVE, 'action':action, 'info':[name, role]})
                    self.socketio.sleep(10)
                elif action == SecretHitler.EXEC_KILL:
                    self.nom_player.gameReply({'state':SecretHitler.STATE_EXECUTIVE, 'action':action, 'dead':1})
                    
                    del self.players[self.nom_player.sid]
                    name = self.nom_player.name
                    
                    self.messagePlayers({'state':SecretHitler.STATE_EXECUTIVE, 'action':action, 'name':name})
                    self.socketio.sleep(5)
                    
                    if self.nom_player.role == HITLER:
                        return self.declareWinners(LIBERAL)
                        
                elif action == SecretHitler.EXEC_ELE:
                    name = self.nom_player.name
                    self.messagePlayers({'state':SecretHitler.STATE_EXECUTIVE, 'action':action, 'name':name})
                    self.socketio.sleep(5)
                    return self.electState(self.nom_player)

        return False

    def declareWinners(self, winners):
        self.messagePlayers({'state':SecretHitler.STATE_END, 'winners':winners})
        return True

    def endState(self):
        print("End")


