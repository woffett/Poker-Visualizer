import pandas as pd
import numpy as np
import holoviews as hv
import param
import paramnb
import sys
from holoviews.util import Dynamic
from bokeh.application import Application
from bokeh.application.handlers import FunctionHandler
from bokeh.layouts import layout, widgetbox, column
from bokeh.models import Select
from bokeh.plotting import curdoc
from parsing import parsing
from sorting import diffCalc

hv.extension('bokeh', 'matplotlib')

GAME = sys.argv[1] if len(sys.argv) > 1 else 'leduc3'
PLAYERS = ['P1','P2']
PLAYER = sys.argv[2] if (len(sys.argv) > 2 and sys.argv[2] in PLAYERS) else 'P1'
GAMEFILE = 'games/%s.txt' % GAME
GAME_SEQ = 'json/%s_sequences.json' % GAME
SORTS = ['diff','square']
SORT = sys.argv[3] if ((len(sys.argv) > 3 and sys.argv[3] in SORTS) or
                       sys.argv[3].startswith('reachIterate=')) else 'diff'
ALGS = sys.argv[4:]
ITERATE = int(SORT[len('reachIterate='):]) if SORT.startswith('reachIterate=') else 500

renderer = hv.renderer('bokeh')

dict_spec = {
    'Curve' : {'plot': {'height': 500, 'width': 500}}
}

hv.opts(dict_spec)

def render(obj):
    plot = renderer.get_plot(obj)
    size = renderer.get_size(plot)
    return renderer._figure_data(plot), size

playerData = dict()  # map of algName -> (p1,p2)
genFunctions = dict()  # map of algName -> genCurvesAlg
tableFunctions = dict() # map of algName -> genTableAlg

def makeGenerator(p1,p2,actions,alg):
    def genCurves(infoset=p1.keys()[0],player=PLAYER,**kwargs):
        '''
        generate the Holoview Curves object corresponding to the infoset
        '''
        iS = p1[infoset] if player == 'P1' else p2[infoset]
        curves = None
        for action in actions:
            xs = [x+1 for x in range(len(iS.probs))]
            ys = [iS.probs[j][action] for j in range(len(iS.probs))]
            curve = hv.Curve((xs,ys),('Iterations','Iterations'),
                             (action,'Probability of '+action),
                             label=action,
                             extents=(0.0,0.0,len(iS.probs),1.0),
                             group=alg)
            if curves == None:
                curves = curve
            else:
                curves = curves * curve
        return curves

    return genCurves
        
def tableGenerator(p1,p2):
    def genTable(infoset=p1.keys()[0],player=PLAYER,**kwargs):
        '''
        generate a Table object containing the reach of the infoset
        '''
        iS = p1[infoset] if player == 'P1' else p2[infoset]
        label = 'Reach at iterate %d for %s' % (ITERATE, iS.alg)
        return hv.Table(([iS.reach[ITERATE]],),[label])
    return genTable

for curAlg in ALGS:

    GAMEDATA = 'json/%s_%s.json' % (GAME, curAlg)
    
    p1,p2,actions = parsing.processInfosets(GAMEFILE)
    parsing.processSeqIDs(p1,p2,GAME_SEQ)
    parsing.getData(p1,p2,actions,GAMEDATA, curAlg)

    playerData[curAlg] = (p1,p2)
    genFunctions[curAlg] = makeGenerator(p1,p2,actions,curAlg)
    tableFunctions[curAlg] = tableGenerator(p1,p2)

def convDmap(iList, alg):
    istream = hv.streams.Stream.define('%s Infoset' % PLAYER,
                                       infoset=iList[0].name)()
    f = genFunctions[alg]
    g = tableFunctions[alg]
    dmap = hv.DynamicMap(f,streams=[istream])
    table = hv.DynamicMap(g,streams=[istream])
    return iList, istream, dmap, table, alg    

depths = dict()  # map of algName -> 2D list of infosets at proper depths
dmaps = []
infosetDicts = []
extractTuple = (lambda(x,y): x) if PLAYER == 'P1' else (lambda(x,y): y)
for algName, tup in playerData.items():
    infosetDicts.append(extractTuple(tup))
diffCalc(infosetDicts,SORT)
arbitrary = infosetDicts[0]

for j in range(max([i.depth for i in arbitrary.values()]) + 1):
    for alg in ALGS:
        if alg not in depths:
            depths[alg] = []
        depths[alg].append([])
        
for infosetDict in infosetDicts:
    for i in infosetDict.values():
        depths[i.alg][i.depth].append(i)

arbitraryDepth = depths.values()[0]
for d in range(len(arbitraryDepth)):
    dmaps.append([])
    for alg in ALGS:
        algDepth = depths[alg]
        algDepth[d].sort(key=lambda i: i.grad, reverse=True)
        curList = algDepth[d]
        if len(curList) > 0:
            dmaps[d].append(convDmap(curList,alg))

dmaps = filter(lambda l : len(l) > 0, dmaps)

def modify_doc(doc):
        # Create HoloViews plot and attach the document

    def getPlots(mapList):
        n = len(mapList)
        iStreams = []
        hvplots = []
        tables = []
        (arbList,arbStream,arbmap,arbTable,arbAlg) = mapList[0]
        for (l,s,d,t,a) in mapList:
            hvplots += [renderer.get_plot(d, doc)]
            tables += [renderer.get_plot(t,doc)]
            iStreams += [s]
        def update(attname, old, new):
            for stream in iStreams:
                stream.event(infoset=new)
        select = Select(title='%s Infosets at Depth %d' %
                        (PLAYER, arbList[0].depth),
                        value=arbList[0].name,
                        options=[i.name for i in arbList],
                        width=200,height=100)
        select.on_change('value',update)
        return select, hvplots, tables

    rows = [getPlots(mapList) for mapList in dmaps]

    # Combine the holoviews plot and widgets in a layout

    matrix = [([widgetbox([s])] + [column([p.state,t.state]) for p,t in zip(plots,tables)]) for (s,plots,tables) in rows]
    
    plot = layout(matrix,sizing_mode='fixed')
    
    doc.add_root(plot)
    return doc

doc = modify_doc(curdoc())
