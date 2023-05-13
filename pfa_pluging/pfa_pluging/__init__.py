from girder import plugin
from girder import events

from girder.models.token import Token
from girder.api.rest import getCurrentUser
from pfa_pluging.Tasks.fibonacci import fibonacci

from girder.api.rest import (
    getCurrentUser,
)

#######################

def call_girder_worker_fibonacci(number, filename, user_fullname, user_email):
   token = Token().createToken(user=getCurrentUser()) 
   async_result = fibonacci.delay(number, 
    filename=filename, 
    user_fullname=user_fullname, 
    user_email=user_email,
    girder_job_title='Fibonacci Job Perso with number'+ str(number),
  	girder_job_type='my_fibo_type',
  	girder_job_public=True,
    girder_client_token=token['_id']
	)

   return async_result.job

def _launchAction1(self):
    event=self  
    filename = event.info['name']
    user_fullname = getCurrentUser()['firstName'] + " " + getCurrentUser()['lastName']
    user_email = getCurrentUser()['email']
    #print('coucou, je vais faire laction')
    number =5    
    call_girder_worker_fibonacci(number, filename, user_fullname, user_email)
    number =15
    call_girder_worker_fibonacci(number, filename, user_fullname, user_email)
    number =25
    call_girder_worker_fibonacci(number, filename, user_fullname, user_email)
    number =26
    call_girder_worker_fibonacci(number, filename, user_fullname, user_email)
    number =27
    call_girder_worker_fibonacci(number, filename, user_fullname, user_email)
    number =28
    call_girder_worker_fibonacci(number, filename, user_fullname, user_email)
    number =29
    call_girder_worker_fibonacci(number, filename, user_fullname, user_email)
    number =30
    call_girder_worker_fibonacci(number, filename, user_fullname, user_email)

class GirderPlugin(plugin.GirderPlugin):
    DISPLAY_NAME = 'pfa_pluging'
    CLIENT_SOURCE_PATH = 'web_client'

    def load(self, info):
        # add plugin loading logic here
        
        # déclencher automatiquement
        #events.bind('model.file.save.after', 'lance une action', _launchAction1)
        
        # evenement déclehncher depuis le bouton iutilisatuer
        # events.bind('model.file.save.after', 'lance une action', _launchAction1)

        print('on passe dans le plugin projet_pfa pour importer la tache')
        pass
