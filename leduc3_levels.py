import pandas as pd
import numpy as np
import holoviews as hv
import param
import paramnb
from holoviews.util import Dynamic
from bokeh.application import Application
from bokeh.application.handlers import FunctionHandler
from bokeh.layouts import layout, widgetbox
from bokeh.models import Select
from bokeh.plotting import curdoc
from parsing import parsing

hv.extension('bokeh', 'matplotlib')

LEDUC3_GAME = 'games/leduc3.txt'
LEDUC3_SEQ = 'json/leduc3_sequences.json'
LEDUC3_CFR = 'json/leduc3_strategies_cfrplus.json'
LEDUC3_EGT = 'json/leduc3_strategies_egt_as.json'

renderer = hv.renderer('bokeh')

dict_spec = {
    'Curve' : {'plot': {'height': 500, 'width': 500}}
}

hv.opts(dict_spec)

def render(obj):
    plot = renderer.get_plot(obj)
    size = renderer.get_size(plot)
    return renderer._figure_data(plot), size

p1C, p2C, actionsC = parsing.processInfosets(LEDUC3_GAME)
parsing.processSeqIDs(p1C,p2C,LEDUC3_SEQ)
parsing.getData(p1C,p2C,actionsC,LEDUC3_CFR)

p1E, p2E, actionsE = parsing.processInfosets(LEDUC3_GAME)
parsing.processSeqIDs(p1E,p2E,LEDUC3_SEQ)
parsing.getData(p1E,p2E,actionsE,LEDUC3_EGT)

def genCurvesCFR(infoset=p1C.keys()[0], player='P1',**kwargs):
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

def genCurvesEGT(infoset=p1E.keys()[0], player='P1',**kwargs):
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
    istream = hv.streams.Stream.define('P1 Infoset', infoset=iList[0].name)()
    if alg == 'CFR':
        dmap = hv.DynamicMap(genCurvesCFR, streams=[istream])
    else:
        dmap = hv.DynamicMap(genCurvesEGT, streams=[istream])
    return iList, istream, dmap

depthsC = []
depthsE = []
for j in range(max([i.depth for i in p1C.values()]) + 1):
    depthsC.append([])
    depthsE.append([])

for i in p1C.values():
    depthsC[i.depth].append(i)
for i in p1E.values():
    depthsE[i.depth].append(i)

dmapsC = [convDmap(l,alg='CFR') for l in depthsC if len(l) > 0]
dmapsE = [convDmap(l,alg='EGT') for l in depthsE if len(l) > 0]

def modify_doc(doc):
        # Create HoloViews plot and attach the document

    def getPlots(infstList, infstream, infstDMap,alg='CFR+'):
        hvplot = renderer.get_plot(infstDMap, doc)
        select = Select(title='P1 %s Infosets at Depth %d' % (alg,infstList[0].depth),
                        value=infstList[0].name,
                        options=[i.name for i in infstList],
                        width=150,height=100)
        select.on_change('value',lambda attname,old,new: infstream.event(infoset=new))
        return hvplot, select

    plotsC = [getPlots(l,s,d,alg='CFR+') for l,s,d in dmapsC]
    plotsE = [getPlots(l,s,d,alg='EGT') for l,s,d in dmapsE]

    # Combine the holoviews plot and widgets in a layout

    zipd = zip(plotsC, plotsE)
    matrix = [[widgetbox([sc,se]),pc.state,pe.state] for ((pc,sc),(pe,se)) in zipd]
    
    plot = layout(matrix,sizing_mode='fixed')
    
    doc.add_root(plot)
    return doc

doc = modify_doc(curdoc())
