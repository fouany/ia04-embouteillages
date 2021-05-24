'''
Created on 4 déc. 2019

@author: cmoulin
An agent for cancelling all services in Redis
The agent has no importance.
Any agent can do that

'''
from agent_v2.service import serviceManager

if __name__ == "__main__":
    print("===============================================================")
    print("SERVICES")
    print("===============================================================")
    serviceManager.printAllServices()
    
    ll = serviceManager.lookupAgents('operation', 'multiplication')
    print(ll)
    serviceManager.cancelService('operation', 'multiplication')
     
    serviceManager.printAllServices()
     
    serviceManager.cancelAll()
    serviceManager.printAllServices()
    print("SERVICES CLEARED")