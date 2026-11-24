#!/usr/bin/python3 -I
import json,sys
d=json.load(open(sys.argv[1],encoding='utf-8'))
def show(o,ind=0,maxs=300):
    if isinstance(o,dict):
        for k,v in o.items():
            if isinstance(v,(dict,list)) and v:
                print(' '*ind+str(k)+':')
                show(v,ind+1,maxs)
            else:
                print(' '*ind+'%s: %s'%(k,json.dumps(v,ensure_ascii=False)[:maxs]))
    elif isinstance(o,list):
        for i,v in enumerate(o):
            if isinstance(v,(dict,list)):
                print(' '*ind+'[%d]'%i)
                show(v,ind+1,maxs)
            else:
                print(' '*ind+json.dumps(v,ensure_ascii=False)[:maxs])
show(d,0,int(sys.argv[2]) if len(sys.argv)>2 else 300)
