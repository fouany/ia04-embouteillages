Classes de base du système MARS
===============================
module cit_fact3/agent_v2/edge_agent.py
---------------------------------------
EdgeBaseAgent : classe de base pour les agents
Définit les connections à Redis
Méthode principale à surcharger : receive_message appelée par on_message
La méthode send_message envoie un message

Une application a besoin d'un fichier de config : edge_settings.ini
à mettre au niveau des boot à lancer
 
module cit_fact3/agent_v2/agent_message.py
------------------------------------------
AgentMessage : structure et méthodes de base pour les messages
Méthodes principales : getContent, setContent
addReceiver ne fonctionne pas. Le champ pour receiver est To qui est une chaine : 1 seul receiver
Il faudrait modifier To (chaine)  en liste. Il faudrait modifier le on_message en conséquence
Utiliser ALL comme nom de receiver pour envoyer à tous les agents sinon le message ne sera envoyé qu'à un seul agent.
requestBaseMessage : prépare un message request
answerMessage : équivallent du createReply de Jade

Le contenu d'un message est installé dans le champ Args["SENTENCE"] du message


module cit_fact3/operation/operation_v2.py
------------------------------------------
BaseAgent : hérite de EdgeBaseAgent
Ce serait mieux de la déplacer dans un module indépendant.
surcharge receive_message pour déclencher la tâche associée à la réception du message
Les noms des tâches des agents sont externalisées dans la class Tasks d'un fichier task_module.py
La classe décrit toutes les tâches de chaque type d'agent.
Exemple de tâche :
{
 'act_name' : 'CONSOLE',
 'act_method' : 'act_console',
 'action_strategy' : 'transfer'
}
Dans cette exemple la méthode act_console sera déclenchée à la réception d'un message de nom CONSOLE.
Une classe d'agents possède une liste de tâches.

Méthode publishService : permet à un agent de souscrire comme service provider 
auprès du ServiceManager (joue le role du DF de Jade)
Méthode filter_strategy : permet de filtrer les actions correspondant à une stratégie

module cit_fact3/agent_v2/service.py
------------------------------------
Définit les classes Service et ServiceManager
Les services ont :
service_type, service_name, agent_className, args
Le serviceManager est accessible dans ce module

Classe ServiceManager
Méthode submitService : permet de publier un service.
Autres méthodes de type lookup pour retrouver des agents fournissant un service.
Autres méthodes pour supprimer des services.
Voir le module test_serviceManager.py pour des exemples.

Démo
====
La démo reprend le td sur l'agent factorielle.
doc/demo_readme.txt décrit les modules à lancer
exemple : lancer les deux commandes suivantes pour avoir une console graphique dans
laquelle on peut donner 1 ou plusieurs factorielles à calculer.
python mainBoot_v2.py
python fact_module.py
Attendre que mainBoot ait créé les agents avant de lancer fact_module. 
Les agents multiplicateurs ont un délai avant de répondre donc l'affichage des résultats peut prendre quelques secondes.
La méthode waker de MultAgent simule un WakerBehaviour et utilise des thread pour cela (voir self.executor = futures.ThreadPoolExecutor(2))
Les calculs de factorielle se font en parallèle.
Les agents multiplicateurs ont un argument supplémentaire qui indiquent jusqu'à quelle valeur ils
peuvent calculer. Ces arguments sont publiés dans les services ce qui fait que l'agent factorielle va chercher
un agent pouvant calculer suivant le produit qu'il doit demander. 10! sera impossible à calculer si les 
multiplicateurs sont limités à 100 000.
Il faut supprimer les services (à l'aide de test_serviceManager.py) si l'on veut chager les arguments à la constructions
des agents multiplicateurs (dans le module mainBoot_v2.py)

Module cit_fact3/agent_v2/utils.py
----------------------------------
classe Publisher : implémente le pattern Obervable (utile pour l'interface graphique)
Elle encapsule une valeur et les listener associés.
Méthodes register, setValue qui déclenche les fonctions enregistrées en tant que listener (par dispatch). 
classe ListPublisher : un ListPublisher envoie déclenche les listeners lorsque une valeur est ajoutée à la liste encapsulée.


Module cit_fact3/fact_module.py
-------------------------------
L'application est créée sur le modèle MVC (FactModel, FactController, FactFrame).
FactModel possède un Publisher.
Le FactController y installe une fonction qui permet d'envoyer un message à l'agent factorielle (dans bindingModelAgent).

Le ConsoleAgent qui sert d'intermédiaire entre le SMA et la console, possède un Publisher qui est mis à jour 
lorsqu'il reçoit une réponse du SMA (résultat d'un factorielle).
Le FactController y installe une fonction qui permet à l'interface de montrer le résultat (dans bindingAgentModel)