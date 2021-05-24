'''
Created on 28 nov. 2019

@author: cmoulin
'''
from tkinter import Tk, Label, Entry, WORD
from tkinter.scrolledtext import ScrolledText
from operation.operation_v2 import ConsoleAgent
from agent_v2.utils import Publisher

class FactFrame(Tk):
    def __init__(self, parent):
        Tk.__init__(self, parent)
        self.title("Factorial - MARS Agents")
        self.initialize()
        
    def initialize(self):
        self.geometry('420x225')
        numberLabel = Label(self,text="Number: \n Ex: 5 10 ...",relief="raised")
        numberLabel.configure(anchor="center", width = 10)
        numberLabel.grid(column=0,row=0,padx=10, pady=10)
        factLabel = Label(self,text="Factorial:",relief="raised")
        factLabel.configure(anchor="center", width = 10)
        factLabel.grid(column=0,row=1,padx=10, pady=10)
        self.numberEntry = Entry(self, bd = 2, width = 50)
        self.numberEntry.grid(column=1,row=0, columnspan = 2, sticky='wns')
        
        self.resultArea = ScrolledText(self, width=37, height=10, wrap=WORD)
        self.resultArea.grid(column=1,row=1,columnspan = 2,sticky = 'wns')


class FactController:
    def __init__(self, factFrame : FactFrame):
        self.view = factFrame
        self.model = FactModel()
        self.initialize()
        
    def initialize(self):
        # create the console agent
        self.agtConsole = ConsoleAgent('console')
        self.bindingViewModel()
        self.bindingModelAgent()
        self.bindingAgentModel()
        
    def bindingViewModel(self):
# if the user clicks on return key askFactorial is activated
        self.view.numberEntry.bind("<Return>", self.askFactorial)
        
# gives the agent the number whose factorial must be calculated     
    def bindingModelAgent(self):
        self.model.factNumberPublisher.register(lambda v: self.agtConsole.sendToMainAgent(v,'fact','FACT'))
         
    def bindingAgentModel(self):
# install a subscriber to the agent publisher. FactResult activated
# when the console agent changes the value in its publisher when it receives
# a n! result from the FactAgent
        self.agtConsole.resultPublisher.register(lambda v: self.factResult(v))
# ask the agent to send a message to the fact agent
# gives the number to the model    
    def askFactorial(self, event):
        numbers = self.view.numberEntry.get()
        #self.agtConsole.setParameter(number)
        self.model.addFact2Calculate(numbers)
# cancel the last result et insert the new one        
    def factResult(self, result):
        self.model.addResult(result)
        self.view.resultArea.insert("end","\n")
        self.view.resultArea.insert("end",result)
        
class FactModel:
    def __init__(self):
        self.factNumberPublisher = Publisher()
        self.calculatedValues = []
        
    def addFact2Calculate(self, numbers):
        numberList = numbers.split()
        for numberStr in numberList:
            self.factNumberPublisher.setValue(int(numberStr))
    
    def addResult(self, factn): 
        self.calculatedValues.append(factn)
        print(self.calculatedValues) 


############### Main programm ###################
############### Needs mainBoot to be launched to      
if __name__ == "__main__":
    frame = FactFrame(None)
    controller = FactController(frame)
    frame.mainloop()