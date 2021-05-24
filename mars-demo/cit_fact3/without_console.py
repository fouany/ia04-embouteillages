'''
Created on 27 nov. 2019

@author: cmoulin
Creates four agents for calculating n!
agtConsole -> receives the user input and display the result
agtFact -> knows how to iterate for calculating n!
agtMult -> knows calculating a * b
agtStore -> stores the values of n! for avoiding twice the same calculus
'''

from operation.operation_v2 import FactAgent, MultAgent, ConsoleAgent, StoreAgent

if __name__ == "__main__":
    agtFact = FactAgent("fact",{})
    args = {}
    args['max'] = 1000
    agtMult1 = MultAgent('mult1',args)
    args['max'] = 10000
    agtMult2 = MultAgent('mult2',args)
    args['max'] = 100000
    agtMult3 = MultAgent('mult3',args)

    ## The following line can be commented. FactAgent does not ask the store agent
    ## in this case. The serviceManager must be empty. Use test_serviceManager for
    # cancelling all registered agents
    agtStore = StoreAgent('store',{})
    
    