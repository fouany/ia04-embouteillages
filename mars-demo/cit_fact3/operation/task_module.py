'''
Created on 28 nov. 2019

@author: cmoulin
'''

class Tasks:
    ACTIONS = {
     'FactAgent' : [{
         'act_name' :'PRODUCT',
         'act_method' : 'act_prod',
         'action_strategy' : 'request'}, # for receiving the product of 2 numbers
         {'act_name' : 'FACT',
          'act_method' : 'act_fact',
          'action_strategy' : 'init'}, # for receiving a request of n!
         {'act_name' : 'STORE',
          'act_method' : 'act_store',
          'action_strategy' : 'persistence' # for receiving an answer of the store agent
         }],
     'MultAgent' : [{
          'act_name' : 'MULTIPLICATION',
          'act_method' : 'act_mult',
          'action_strategy' : 'product'
        }],
      'ConsoleAgent' : [{
          'act_name' : 'CONSOLE',
          'act_method' : 'act_console',
          'action_strategy' : 'transfer'
        }],
       'StoreAgent' : [
           {'act_name' :'IS_STORED',
            'act_method' : 'act_is_stored',
            'action_strategy' : 'exist'},
          {'act_name' : 'STORE',
            'act_method' : 'act_store',
            'action_strategy' : 'persistence'}]
     }

