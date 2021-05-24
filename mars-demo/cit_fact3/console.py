'''
Created on 12 déc. 2019

@author: cmoulin
'''
from operation.operation_v2 import ConsoleAgent
if __name__ == "__main__":
    agtConsole = ConsoleAgent('console')
    
    print("===============================================================")
    print("INPUT CONSOLE")
    print("===============================================================")
    
    question = ''
    while question != 'q':
          
        n = input("Fact:") 
        agtConsole.sendToMainAgent(n,'fact','FACT')
          
        question = input("Exit: q [enter] Else go on")
