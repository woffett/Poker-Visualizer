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

infosetCFR = hv.streams.Stream.define('P1 Infoset', infoset=p1C.keys()[0])()
dmapCFR = hv.DynamicMap(genCurvesCFR, streams=[infosetCFR])

infosetEGT = hv.streams.Stream.define('P1 Infoset', infoset=p1E.keys()[0])()
dmapEGT = hv.DynamicMap(genCurvesEGT, streams=[infosetEGT])

def modify_doc(doc):
    # Create HoloViews plot and attach the document
    hvplotCFR = renderer.get_plot(dmapCFR, doc)
    hvplotEGT = renderer.get_plot(dmapEGT, doc)

    def CFR_update(attrname, old, new):
        infosetCFR.event(infoset=new)
        
    selectCFR = Select(title='Player 1 Infosets for CFR+',
                       value=p1C.keys()[0],options=p1C.keys(),
                       width=150,height=100)
    selectCFR.on_change('value', CFR_update)

    def EGT_update(attrname, old, new):
        infosetEGT.event(infoset=new)
            
    selectEGT = Select(title='Player 1 Infosets for EGT',
                       value=p1E.keys()[0],options=p1E.keys(),
                       width=150, height=100)
    selectEGT.on_change('value', EGT_update)

    wbox = widgetbox([selectCFR, selectEGT])

    # Combine the holoviews plot and widgets in a layout
    plot = layout([
        [wbox, hvplotCFR.state, hvplotEGT.state]
    ], sizing_mode='fixed')
    
    doc.add_root(plot)
    return doc

doc = modify_doc(curdoc())
