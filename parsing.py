import re
import sys
from infoset import InfoSet, P1, P2

def getSearchParam(infoset, parent=False):

    chancePos = infoset.ID.find('?')
    isP1 = (chancePos == len(infoset.ID) - 1 or
            infoset.ID[chancePos+1] == '/')
    if isP1:
        chanceCards = infoset.ID[chancePos-1:chancePos+1]
    else:
        chanceCards = infoset.ID[chancePos:chancePos+2]

    if parent:
        turns = infoset.ID.split('/')
        lastMove = turns[-1]
        parentSet = re.match('(.+):(.+)', lastMove).groups()[0]
        if parentSet == 'C':  # chance!
            parentFormat = '/'.join(infoset.ID.split('/')[:-2])
        else:
            parentFormat = '/'.join(infoset.ID.split('/')[:-1])
        return parentFormat.replace(chanceCards, '([JKQ\?]+?)') + '$'
    else:
        IDFormat = infoset.ID.replace(chanceCards, '([JKQ\?]+?)')
        #  we also need to make sure that we have the "C" in front for the first chance node
        if IDFormat[1] != 'C':
            IDFormat = '/C:' + IDFormat[1:]
        return 'node ' + IDFormat + ' player(.+)actions (.+)'
    
def addFamily(infoset, parentSets):
    '''
    add the possible parents of infoset
    add infoset to the possible children of all of its parents
    '''

    isRoot = len(infoset.ID.split('/')) <= 2
    
    if isRoot:
        return

    searchParam = getSearchParam(infoset, parent=True)
    regex = re.compile(searchParam)
    
    for parentID in parentSets.keys():
        if regex.match(parentID):
            infoset.parents.add(parentID)
            parentSets[parentID].children.add(infoset.ID)


def addAllFamily(p1Sets, p2Sets):
    '''
    add the possible parents and children of each infoset
    '''

    for infoset in p1Sets.values():
        addFamily(infoset, p1Sets)
        addFamily(infoset, p2Sets)

    for infoset in p2Sets.values():
        addFamily(infoset, p1Sets)
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
        raise Exception('Failed to add action for infoset: %s' % infoset.ID)
    for action in actions.split(' '):
        if action != '':
            infoset.actions.add(action)

        
def addAllActions(pInfoSets,f):
    '''
    add actions for all the infosets from a game file
    '''

    for infoset in pInfoSets.values():
        addActions(infoset, f)


def process(filename):
    '''
    read all the infosets from a game file
    '''

    #  {p1/p2}Nodes are dictionaries mapping InfoSet IDs to InfoSets
    p1Sets = dict() 
    p2Sets = dict()
    
    f = open(filename)

    for line in f:
        isInfoSet = re.match('infoset(.+)',line)
        if isInfoSet:
            line = line[:-1]  # to get rid of the trailing newline
            curIS = InfoSet(line)
            if curIS.player == P1:
                p1Sets[curIS.ID] = curIS
            else:
                p2Sets[curIS.ID] = curIS

    #  Now the nodes are missing a couple of attributes: parents, children, actions, and probs
    addAllFamily(p1Sets, p2Sets)
    addAllActions(p1Sets,f)
    addAllActions(p2Sets,f)

    f.close()

    return p1Sets, p2Sets
            

if __name__ == '__main__':
    if len(sys.argv) > 1:
        gameFile = sys.argv[1]
        try:
            p1, p2 = process(gameFile)
            print('Processing successful!')
        except Exception as e:
            print('Failed to process gamefile! Error: ' + str(e))
    else:
        print('Provide a game file as an argument! ')

        
