DIFF = lambda (x,y): abs(x-y)
SQUAREDIFF = lambda(x,y): (x-y)**2
FNDICT = {'diff': DIFF, 'square': SQUAREDIFF}

def diffCalc2(alg1Infosets, alg2Infosets, f='diff'):

    infosetNames = alg1Infosets.keys()
    fn = FNDICT.get(f)
    if not fn:
        fn = DIFF

    for infosetName in infosetNames:
        a1 = alg1Infosets[infosetName]
        a2 = alg2Infosets[infosetName]
        actions = a1.actions
        diff = 0.0
        for i in range(len(a1.probs)):
            for curAct in actions:
                diff += fn((a1.probs[i][curAct],a2.probs[i][curAct]))
        a1.grad = diff
        a2.grad = diff

def diffCalc(infosetDicts,f='diff'):

    infosetNames = infosetDicts[0].keys()
    fn = FNDICT.get(f)
    if not fn:
        fn = DIFF

    for infosetName in infosetNames:
        data = []
        for infosetDict in infosetDicts:
            data.append(infosetDict[infosetName])

        if (f.startswith('reachIterate=')):
            reachIt = int(f[len('reachIterate='):])
            for infoset in data:
                infoset.grad = (infoset.reach[reachIt-1] if ((reachIt-1) >= 0 and
                                                            (reachIt-1) <
                                                            len(infoset.reach))
                                else infoset.reach[-1])
                
        else:
            arbitrary = data[0]
            actions = arbitrary.actions
            diff = 0.0
            for i in range(len(data)):
                for j in range(i+1,len(data)):
                    a1 = data[i]
                    a2 = data[j]
                    diff = 0.0
                    for iterate in range(len(a1.probs)):
                        for curAct in actions:
                            diff += fn((a1.probs[iterate][curAct],
                                        a2.probs[iterate][curAct]))

                    a1.grad = max(a1.grad, diff)
                    a2.grad = max(a2.grad, diff)
                
        
