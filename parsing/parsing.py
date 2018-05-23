import json
import math
import re
import sys
from infoset import InfoSet, P1, P2

NAN = float('NaN')
GRADIENT_ITS = 1.0/3.0

def getSearchParam(infoset, parent=False):

    chancePos = infoset.name.find('?')
    isP1 = (chancePos == len(infoset.name) - 1 or
            infoset.name[chancePos+1] == '/')
    if isP1:
        chanceCards = infoset.name[chancePos-1:chancePos+1]
    else:
        chanceCards = infoset.name[chancePos:chancePos+2]
    nameFormat = infoset.name.replace(chanceCards, '([JKQ\?]+?)')
    #  we also need to make sure that we have the "C" in front for the first chance node
    if nameFormat[1] != 'C':
        nameFormat = '/C:' + nameFormat[1:]
    return 'node ' + nameFormat + ' player(.+)actions (.+)'
    
def addFamily(infoset, parentSets):
    '''
    add each infoset to its parent's set of children
    '''

    isRoot = len(infoset.name.split('/')) <= 2
    
    if isRoot:
        return
    else:
        parent = parentSets.get(infoset.parent, None)
        if parent:
            parent.addChildren(infoset.name)

def addAllFamily(p1Sets, p2Sets):
    '''
    add the possible parents and children of each infoset
    '''

    for infoset in p1Sets.values():
        addFamily(infoset, p1Sets)

    for infoset in p2Sets.values():
        addFamily(infoset, p2Sets)
    
        
def addActions(infoset, f):
    '''
    add actions for a particular infoset from a game file
    '''

    f.seek(0,0)

    searchParam = getSearchParam(infoset)
    regex = re.compile(searchParam)
    for line in f:
        matchObj = regex.match(line)
        if matchObj:
            break
    try:
        actions = matchObj.groups()[-1]  # obtain the last string + delete the extra '\n'
    except Exception as e:
        raise Exception('Failed to add action for infoset: %s' % infoset.name)
    for action in actions.split(' '):
        if action != '':
            infoset.actions.add(action)

        
def addAllActions(pInfoSets,f, actions):
    '''
    add actions for all the infosets from a game file, and add them into a set of actions
    '''

    for infoset in pInfoSets.values():
        addActions(infoset, f)
        for action in infoset.actions:
            actions.add(action)


def processInfosets(filename):
    '''
    read all the infosets from a game file
    returns dictionaries mapping infoset names to infoset objects,
    and a set of action names
    '''

    #  {p1/p2}Nodes are dictionaries mapping InfoSet names to InfoSets
    p1Sets = dict() 
    p2Sets = dict()
    actions = set()
    
    f = open(filename)

    for line in f:
        isInfoSet = re.match('infoset(.+)',line)
        if isInfoSet:
            line = line[:-1]  # to get rid of the trailing newline
            curIS = InfoSet(line)
            if curIS.player == P1:
                p1Sets[curIS.name] = curIS
            else:
                p2Sets[curIS.name] = curIS

    #  Now the nodes are missing a couple of attributes: parents, children, actions, and probs
    addAllFamily(p1Sets, p2Sets)
    addAllActions(p1Sets,f, actions)
    addAllActions(p2Sets,f, actions)

    f.close()

    return p1Sets, p2Sets, actions


def processSeqIDs(p1Sets, p2Sets, seqFilename):
    '''
    read sequence IDs from seqFilename into p1/p2Sets
    write mapping of sequence IDs to infoset and action names into each
    infoset in p1Sets and p2Sets
    '''

    f = open(seqFilename)
    jObj = json.load(f)
    d = json.JSONDecoder().decode(json.dumps(jObj))
    f.close()

    p1Seqs = d['player1']
    p2Seqs = d['player2']

    for seqDict in p1Seqs:
        if seqDict['is_empty_sequence']:
            continue
        seqID = seqDict['sequence_id']
        seqName = seqDict['infoset_name']
        actionName = seqDict['action_name']
        p1Sets[seqName].seqIDs[seqID] = actionName

    for seqDict in p2Seqs:
        if seqDict['is_empty_sequence']:
            continue
        seqID = seqDict['sequence_id']
        seqName = seqDict['infoset_name']
        actionName = seqDict['action_name']
        p2Sets[seqName].seqIDs[seqID] = actionName


def alreadyAddedIt(itDict, isDicts, sampSize=1.0):
    '''
    returns true if the particular iterate in question has already
    been added to the infosets in isDicts
    '''

    itNumber = itDict['iteration']
    randIS = isDicts.values()[0]
    const = int(math.floor(sampSize**(-1)))
    return len(randIS.probs)*const >= itNumber

def normalize(isDicts, actions):
    '''
    Normalize the probabilities for the last 
    probability distributions added to each infoset,
    also adds the reach for the current iteration to
    each infoset's reach list
    '''

    for infoset in isDicts.values():
        lastIt = infoset.probs[-1]
        total = sum([x for x in lastIt.values()])
        normalized = dict()
        reach = 0.0
        for action, prob in lastIt.items():
            reach += prob
            normalized[action] = prob/total
        for action in actions:
            if action not in infoset.actions:
                normalized[action] = -1.0
        infoset.probs[-1] = normalized
        infoset.reach.append(reach)

        
def getReach(isDicts):
    '''
    Use the un-normalized probabilities in the last 
    iterate of each infoset to calculate the
    reach for that infoset at that iteration,
    and append it to the appropriate infoset's reach list
    '''

    for infoset in isDicts.values():
        lastIt = infoset.probs[-1]
        curReach = 0.0
        for action, prob in lastIt.items():
            curReach += prob
        infoset.reach.append(curReach)
    

def addIterate(itDict, isDicts, actions, alg):
    '''
    adds the strategy profiles for the iterate represented by itDict
    to the infosets in isDicts
    for all actions not in the infoset, add them to probs as NaN
    also add alg as an attribute of each infoset
    '''

    strategies = itDict['strategy']

    for infoset in isDicts.values():
        curIt = dict()
        for seqID, action in infoset.seqIDs.items():
            curIt[action] = strategies[seqID]
        infoset.probs.append(curIt)
        infoset.alg = alg

    getReach(isDicts)
    normalize(isDicts, actions)
    

def getData(p1Sets, p2Sets, actions, dataFilename, alg, its=None):
    '''
    extracts iterate data from dataFilename for the particular player,
    adding it to the infosets in infosetDict
        - if its is provided as an argument, only adds up to its number
          of iterates for each player
    also adds alg as an attribute of each dataset
    '''

    f = open(dataFilename)
    jObj = json.load(f)
    itList = json.JSONDecoder().decode(json.dumps(jObj))
    f.close()

    lim = (len(itList) if (its == None or its < 0 or 2*its > len(itList))
           else 2*its)

    for i in range(lim):
        curDict = itList[i]
        curSets = p1Sets if curDict['player_id'] == 1 else p2Sets
        if alreadyAddedIt(curDict,curSets):
            continue
        addIterate(curDict,curSets, actions, alg)

    for infs in p1Sets.values():
        infs.getAvgGrad(min(1, int(math.ceil(GRADIENT_ITS*lim))))
        
    for infs in p2Sets.values():
        infs.getAvgGrad(min(1, int(math.ceil(GRADIENT_ITS*lim))))
        

if __name__ == '__main__':
    if len(sys.argv) > 1:
        gameFile = sys.argv[1]
        try:
            p1, p2, actions = process(gameFile)
            print('Processing successful!')
        except Exception as e:
            print('Failed to process gamefile! Error: ' + str(e))
    else:
        print('Provide a game file as an argument! ')

