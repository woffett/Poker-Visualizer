import pandas as pd
import numpy as np
import holoviews as hv
import param
import paramnb
import sys
from holoviews.util import Dynamic
from bokeh.application import Application
from bokeh.application.handlers import FunctionHandler
from bokeh.layouts import layout, widgetbox
from bokeh.models import Select
from bokeh.plotting import curdoc
from parsing import parsing

hv.extension('bokeh', 'matplotlib')

GAME = sys.argv[1] if len(sys.argv) > 1 else 'leduc3'
PLAYERS = ['P1','P2']
PLAYER = sys.argv[2] if (len(sys.argv) > 2 and sys.argv[2] in PLAYERS) else 'P1'
GAMEFILE = 'games/%s.txt' % GAME
GAME_SEQ = 'json/%s_sequences.json' % GAME
GAME_CFR = 'json/%s_strategies_cfrplus.json' % GAME
GAME_EGT = 'json/%s_strategies_egt_as.json' % GAME

renderer = hv.renderer('bokeh')

dict_spec = {
    'Curve' : {'plot': {'height': 500, 'width': 500}}
}

hv.opts(dict_spec)

def render(obj):
    plot = renderer.get_plot(obj)
    size = renderer.get_size(plot)
    return renderer._figure_data(plot), size

p1C, p2C, actionsC = parsing.processInfosets(GAMEFILE)
parsing.processSeqIDs(p1C,p2C,GAME_SEQ)
parsing.getData(p1C,p2C,actionsC,GAME_CFR)

p1E, p2E, actionsE = parsing.processInfosets(GAMEFILE)
parsing.processSeqIDs(p1E,p2E,GAME_SEQ)
parsing.getData(p1E,p2E,actionsE,GAME_EGT)

def genCurvesCFR(infoset=p1C.keys()[0] if PLAYER=='P1' else p2C.keys()[0], player=PLAYER,**kwargs):
    '''
    generate the Holoview Curves object corresponding to the infoset
    '''
    iS = p1C[infoset] if player == 'P1' else p2C[infoset]
    curves = None
    for action in actionsC:
        xs = [x+1 for x in range(len(iS.probs))]
        ys = [iS.probs[j][action] for j in range(len(iS.probs))]
        curve = hv.Curve((xs,ys),('Iterations','Iterations'),
                         (action,'Probability of '+action),
                         label=action,
                         extents=(0.0,0.0,len(iS.probs),1.0),
                         group='CFR+ Strategies')
        if curves == None:
            curves = curve
        else:
            curves = curves * curve
    return curves

def genCurvesEGT(infoset=p1E.keys()[0] if PLAYER=='P1' else p2E.keys()[0], player=PLAYER,**kwargs):
    '''
    generate the Holoview Curves object corresponding to the infoset
    '''
    iS = p1E[infoset] if player == 'P1' else p2E[infoset]
    curves = None
    for action in actionsE:
        xs = [x+1 for x in range(len(iS.probs))]
        ys = [iS.probs[j][action] for j in range(len(iS.probs))]
        curve = hv.Curve((xs,ys),
                         ('Iterations','Iterations'),
                         (action,'Probability of '+action),
                         label=action,
                         extents=(0.0,0.0,len(iS.probs),1.0),
                         group='EGT Strategies')
        if curves == None:
            curves = curve
        else:
            curves = curves * curve
    return curves

def convDmap(iList, alg='CFR'):
    istream = hv.streams.Stream.define('%s Infoset' % PLAYER, infoset=iList[0].name)()
    if alg == 'CFR':
        dmap = hv.DynamicMap(genCurvesCFR, streams=[istream])
    else:
        dmap = hv.DynamicMap(genCurvesEGT, streams=[istream])
    return iList, istream, dmap, alg

depthsC = []
depthsE = []


if PLAYER == 'P1':
    for j in range(max([i.depth for i in p1C.values()]) + 1):
        depthsC.append([])
        depthsE.append([])
    for i in p1C.values():
        depthsC[i.depth].append(i)
    for i in p1E.values():
        depthsE[i.depth].append(i)
else:
    for j in range(max([i.depth for i in p2C.values()]) + 1):
        depthsC.append([])
        depthsE.append([])
    for i in p2C.values():
        depthsC[i.depth].append(i)
    for i in p2E.values():
        depthsE[i.depth].append(i)

dmapsC = [convDmap(l,alg='CFR') for l in depthsC if len(l) > 0]
dmapsE = [convDmap(l,alg='EGT') for l in depthsE if len(l) > 0]

def modify_doc(doc):
        # Create HoloViews plot and attach the document

    def getPlots(iList1, iStream1, dmap1, alg1,
                 iList2, iStream2, dmap2, alg2):
        hvplot1 = renderer.get_plot(dmap1, doc)
        hvplot2 = renderer.get_plot(dmap2, doc)
        def update(attname, old, new):
            iStream1.event(infoset=new)
            iStream2.event(infoset=new)
        select = Select(title='%s Infosets at Depth %d' % (PLAYER,
                                                           iList1[0].depth),
                        value=iList1[0].name,
                        options=[i.name for i in iList1],
                        width=200,height=100)
        select.on_change('value',update)
        return select, hvplot1, hvplot2

    plots = zip(dmapsC,dmapsE)
    rows = [getPlots(l1,s1,d1,a1,l2,s2,d2,a2) for ((l1,s1,d1,a1),
                                                   (l2,s2,d2,a2)) in plots]

    # Combine the holoviews plot and widgets in a layout

    matrix = [[widgetbox([s]),pc.state,pe.state] for (s,pc,pe) in rows]
    
    plot = layout(matrix,sizing_mode='fixed')
    
    doc.add_root(plot)
    return doc

doc = modify_doc(curdoc())
