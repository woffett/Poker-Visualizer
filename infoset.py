import re

P1 = 'P1'
P2 = 'P2'

class InfoSet():

    def __init__(self, gameFileLine):
        self.line = gameFileLine
        self.ID = self.getID(gameFileLine)
        self.player = self.getPlayer()
        self.members = self.getMembers()
        self.depth = self.getDepth()
        self.parent = self.getParent()
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

    def getParent(self):
        '''
        returns the ID of the infoset's parent node in the decision tree
        '''

        isRoot = len(self.ID.split('/')) <= 2

        if isRoot:
            return ''
        else:
            return '/'.join(self.ID.split('/')[:-2])

    def getDepth(self):
        '''
        returns the infoset's depth in the game tree
        NOTE - depth is not for the decision tree
        '''
        return self.ID.count('/') - 1

    ##### ADD methods for adding data to the infoset #####

    def addParent(self, parentID):
        self.parents.add(parentID)

    def addChildren(self, childID):
        self.children.add(childID)

    def addAction(self,s):
        self.actions.add(s)

    def setProbs(self, action, prob):
        if action not in self.actions:
            self.addAction(action)
        self.probs[action] = prob

    ##### MISC methods #####

    def __hash__(self):
        return hash(self.ID)

    def toDict(self):
        '''
        returns a dictionary that maps string representation of the object
        attributes to string representations of their values
        '''
        res = dict()

        res['ID'] = self.ID
        res['player'] = self.player
        res['members'] = ' '.join(list(self.members))
        res['parent'] = self.parent
        res['children'] = ' '.join(list(self.children)) if len(self.children) > 0 else ''
        res['depth'] = str(self.depth)
        res['actions'] = ' '.join(list(self.actions))

        return res
        
