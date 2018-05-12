import pandas as pd
import numpy as np
import holoviews as hv
import parsing
import sys
hv.extension('bokeh', 'matplotlib')

KUHN_GAME = 'games/kuhn.txt'
KUHN_SEQ = 'json/kuhn_sequences.json'
KUHN_DATA = 'json/kuhn_datapoints.json'
LEDUC3_GAME = 'games/leduc3.txt'
LEDUC3_SEQ = 'json/leduc3_sequences.json'
LEDUC3_DATA = 'json/leduc3_datapoints.json'

def genCurves(infoset):
    '''
    generate the Holoview Curves object corresponding to the infoset
    '''
    curves = None
    for action in infoset.actions:
        xs = [x+1 for x in range(len(infoset.probs))]
        ys = [infoset.probs[j][action] for j in range(len(infoset.probs))]
        curve = hv.Curve((xs,ys),
                         ('Iterations','Iterations'),
                         (action,'Probability of '+action),
                         label=action)
        if curves == None:
            curves = curve
        else:
            curves = curves * curve
    return curves

def makeOutput(game):

    gameFile = 'games/%s.txt' % game
    seqFile = 'json/%s_sequences.json' % game
    dataFile = 'json/%s_datapoints.json' % game
    
    p1, p2 = parsing.processInfosets(gameFile)
    parsing.processSeqIDs(p1, p2, seqFile)
    parsing.getData(p1, p2, dataFile)
    '''
    hm1 = hv.HoloMap({(i.player,name): genCurves(i)
                      for p in (p1,p2)
                      for name,i in p.items()},
                     kdims=['player','infoset'])
    '''
    p1 = hv.HoloMap({name: genCurves(i) for name,i in p1.items()},
                    kdims=['infoset'])
    p2 = hv.HoloMap({name: genCurves(i) for name,i in p2.items()},
                    kdims=['infoset'])
    grid1 = hv.GridSpace(p1)
    grid2 = hv.GridSpace(p2)

    layout1 = hv.NdLayout(grid1).cols(2)
    layout2 = hv.NdLayout(grid2).cols(2)
    hv.output(layout1 + layout2, size=150, filename=game)
    

if __name__ == '__main__':
    if len(sys.argv) > 1:
        game = sys.argv[1]
        makeOutput(game)
    else:
        print('Please provide a game to analyze!')        
