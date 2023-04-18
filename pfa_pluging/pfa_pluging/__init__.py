from girder import plugin
from girder import events

from girder.models.token import Token
from girder.api.rest import getCurrentUser
from gwexample.analyses.tasks import fibonacci
from pfa_pluging.Tasks.progress import progressTest

from girder.api.rest import (
    getCurrentUser,
)

#######################

def call_girder_worker_fibonacci(number):
   #async_result = fibonacci.delay(  number,  girder_job_title="A Custom Job Title")
    # Create a token with permissions of the current user.
   token = Token().createToken(user=getCurrentUser()) 
   #.apply_async(countdown=60)
   async_result =fibonacci.delay(number,
    girder_job_title='Fibonacci Job Perso with number'+ str(number),
  	girder_job_type='my_fibo_type',
  	girder_job_public=True,
    girder_client_token=token['_id']
	)

   return async_result.job

def _launchAction1(self):
    event=self  
    
    #print('coucou, je vais faire laction')
    number =5    
    call_girder_worker_fibonacci(number)
    number =15
    call_girder_worker_fibonacci(number)
    number =25
    call_girder_worker_fibonacci(number)
    number =26
    call_girder_worker_fibonacci(number)
    number =27
    call_girder_worker_fibonacci(number)
    number =28
    call_girder_worker_fibonacci(number)
    number =29
    call_girder_worker_fibonacci(number)
    number =30
    call_girder_worker_fibonacci(number)

def call_girder_worker_progress(number):
   #async_result = fibonacci.delay(  number,  girder_job_title="A Custom Job Title")
    # Create a token with permissions of the current user.
   token = Token().createToken(user=getCurrentUser())
   #.apply_async(countdown=60)
   async_result = progressTest.delay( number, girder_job_title='Progress Job Perso with number'+ str(number),
          girder_job_type='my_progress_type',
          girder_job_public=True,
    girder_client_token=token['_id']
        )  

def _launchAction2(self):
    print("############################################################")
    event=self
    number =5    
    job=call_girder_worker_progress(number)
    print(job)
    number =10    
    job=call_girder_worker_progress(number)
    print(job)
    number =15    
    job=call_girder_worker_progress(number)
    print(job)
    number =20    
    job=call_girder_worker_progress(number)
    print(job)


class GirderPlugin(plugin.GirderPlugin):
    DISPLAY_NAME = 'projet_pfa'
    CLIENT_SOURCE_PATH = 'web_client'

    def load(self, info):
        # add plugin loading logic here
        
        # déclencher automatiquement
        #events.bind('model.file.save.after', 'lance une action', _launchAction1)
        
        # evenement déclehncher depuis le bouton iutilisatuer
        events.bind('model.file.save.after', 'lance une action', _launchAction1)

        print('on passe dans le plugin projet_pfa pour importer la tache')
        pass
