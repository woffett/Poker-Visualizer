import math
import re

P1 = 'P1'
P2 = 'P2'

class InfoSet():

    def __init__(self, gameFileLine):
        self.line = gameFileLine
        self.name = self.getName(gameFileLine)
        self.player = self.getPlayer()
        self.members = self.getMembers()
        self.depth = self.getDepth()
        self.parent = self.getParent()
        self.children = set()
        self.actions = set()
        self.seqIDs = dict()
        self.probs = []
        self.grad = 0.0
        self.alg = ''


    ##### GET methods for retrieving info set data #####

    def getName(self, gameFileLine):
        '''
        returns the InfoSet's name
        '''
        regMatch = re.match('infoset (.+?) nodes (.*)', gameFileLine)
        return regMatch.groups()[0]

    def getPlayer(self):
        '''
        returns the InfoSet's player (the one yet to make a move)
        '''
        lastTurn = self.name.split('/')[-1]
        regMatch = re.match('(.+?):(.+)', lastTurn)
        if regMatch:
            lastPlayer = regMatch.groups()[0]
            return P2 if lastPlayer == P1 else P1
        else:
            return P1

    def getMembers(self):
        '''
        returns a set of node names for the members of this infoset
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

    def getParent(self):
        '''
        returns the name of the infoset's parent node in the decision tree
        '''

        isRoot = len(self.name.split('/')) <= 2

        if isRoot:
            return ''
        else:
            return '/'.join(self.name.split('/')[:-2])

    def getDepth(self):
        '''
        returns the infoset's depth in the game tree
        NOTE - depth is not for the decision tree
        '''
        return self.name.count('/') - 1

    def getAvgGrad(self, numIts):
        '''
        sets own grad attribute to the highest gradient across
        its probabilities for the actions at the infoset,
        between the 0th index and the (numIts)'th index in
        self.probs
        '''
        probDiffs = dict()
        for a in self.actions:
            probDiffs[a] = abs(self.probs[0][a] - self.probs[numIts][a])

        self.grad = max(probDiffs.values())

    ##### ADD methods for adding data to the infoset #####

    def addParent(self, parentName):
        self.parents.add(parentName)

    def addChildren(self, childName):
        self.children.add(childName)

    def addAction(self,s):
        self.actions.add(s)
        self.probs[s] = []

    def setProbs(self, action, prob):
        if action not in self.actions:
            self.addAction(action)
        self.probs[action].append(prob)

    ##### MISC methods #####

    def __hash__(self):
        return hash(self.name)

    def toDict(self):
        '''
        returns a dictionary that maps string representation of the object
        attributes to string representations of their values
        '''
        res = dict()

        res['ID'] = self.name
        res['player'] = self.player
        res['members'] = ' '.join(list(self.members))
        res['parent'] = self.parent
        res['children'] = ' '.join(list(self.children)) if len(self.children) > 0 else ''
        res['depth'] = str(self.depth)
        res['actions'] = ' '.join(list(self.actions))

        return res
        
