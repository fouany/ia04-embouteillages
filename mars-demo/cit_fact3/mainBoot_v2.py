'''
Created on 6 déc. 2019

@author: cmoulin
'''
from operation.operation_v2 import FactAgent, MultAgent, ConsoleAgent, StoreAgent

if __name__ == "__main__":
    agtFact = FactAgent("fact")
    args = {}
    args['max'] = 1000
    agtMult1 = MultAgent('mult1',args)
    args['max'] = 10000
    agtMult2 = MultAgent('mult2',args)
    args['max'] = 100000
    agtMult3 = MultAgent('mult3',args)
    agtStore = StoreAgent('store')