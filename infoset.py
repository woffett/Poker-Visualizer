import re

P1 = 'P1'
P2 = 'P2'

class InfoSet():

    def __init__(self, gameFileLine):
        self.line = gameFileLine
        self.ID = self.getID(gameFileLine)
        self.player = self.getPlayer()
        self.members = self.getMembers()
        self.parents = set()
        self.children = set()
        self.actions = set()
        self.probs = dict()

    ##### GET methods for retrieving info set data #####

    def getID(self, gameFileLine):
        '''
        returns the InfoSet's ID
        '''
        regMatch = re.match('infoset (.+?) nodes (.*)', gameFileLine)
        return regMatch.groups()[0]

    def getPlayer(self):
        '''
        returns the InfoSet's player (the one yet to make a move)
        '''
        lastTurn = self.ID.split('/')[-1]
        regMatch = re.match('(.+?):(.+)', lastTurn)
        if regMatch:
            lastPlayer = regMatch.groups()[0]
            return P2 if lastPlayer == P1 else P1
        else:
            return P1

    def getMembers(self):
        '''
        returns a set of node IDs for the members of this infoset
        '''
        result = set()
        regMatch = re.match('(.+)nodes (.+)', self.line)
        try:
            members = regMatch.groups()[1]
        except:
            raise Exception('Failed to parse members from line %s' % self.line)
        for m in members.split(' '):
            result.add(m)
        return result
        

    ##### ADD methods for adding data to the infoset #####

    def addParent(self,n):
        self.parents[n.ID] = n

    def addChildren(self,n):
        self.children[n.ID] = n

    def addAction(self,s):
        self.actions.add(s)

    def setProbs(self, action, prob):
        if action not in self.actions:
            self.addAction(action)
        self.probs[action] = prob

    ##### MISC methods #####

    def __hash__(self):
        return hash(self.ID)
