from girder import plugin
from girder import events

from girder_jobs.constants import JobStatus
from girder.api.rest import getCurrentUser
from girder_worker_utils.decorators import argument
from girder_worker_utils import types
from string import Template
from girder.utility import mail_utils

#######################

def read_mail_template(filename):
    '''
    Reads the 'filename' mail template.
    '''
    with open(filename, 'r', encoding='utf-8') as template_file:
        template_file_content = template_file.read()
    return Template(template_file_content)

@argument('job_name', types.String, min=1, max=1)
@argument('start_hour', types.String, min=1, max=1)
@argument('processed_file', types.String, min=1, max=1)
@argument('end_job', types.String, min=1, max=1)
def mail_sender(job_name, start_hour, processed_file, end_job, user):
    '''
    Sends a mail to the current user running the job with some log information:
    - the user fullname;
    - the job name;
    - the job launching start hour;
    - the processed file name;
    - the final job state.
    '''
    print('####################')
    print('mail_sender')
    print('####################')

    if user['email'] is not None and mail_utils.validateEmailAddress(user['email']):
        message_template = read_mail_template('mymessage.txt')
        message = message_template.substitute(PERSON_NAME=user['firstName'] + " " + user['lastName'], JOB_NAME=job_name, START_HOUR=start_hour, PROCESSED_FILE=processed_file, END_JOB=end_job)
        mail_utils.sendMail(subject='My mail from girder', text=message, to=user['email'])
    else:
        print("send_mail_error")

def validateJobStatus(event):
    if event.info == 1234:
        event.preventDefault().addResponse(True)
        print('event.info == 1234')

    if event.info == JobStatus.INACTIVE:
      print('event.info == INACTIVE (0)')
    elif event.info == JobStatus.QUEUED:
       print('event.info == QUEUED (1)')   
    elif event.info == JobStatus.RUNNING:     
       print('event.info == RUNNING (2) ')
    elif event.info == JobStatus.SUCCESS:     
      print('event.info == SUCCESS (3) ') 
      # mail_sender(self.name.split(".")[0], event.info['created'].strftime("%H:%M:%S"), event.info['name'], "SUCCESS", getCurrentUser())
    elif event.info == JobStatus.ERROR:     
      print('event.info == ERROR (4) ')    
      # mail_sender(self.name.split(".")[0], event.info['created'].strftime("%H:%M:%S"), event.info['name'], "SUCCESS", getCurrentUser())
    elif event.info == JobStatus.CANCELED:     
      print('event.info == CANCELED (5)  ') 
      # mail_sender(self.name.split(".")[0], event.info['created'].strftime("%H:%M:%S"), event.info['name'], "CANCELED", getCurrentUser())
    else:
        print('event.info == X')   
        
class GirderPlugin(plugin.GirderPlugin):
    DISPLAY_NAME = 'downstream_pluging'  
    CLIENT_SOURCE_PATH = 'web_client'
   
    # downstream plugin
    def load(self, info):
        # add plugin loading logic here
        #print('on passe dans le plugin RMSBPlugin pour importer la tache')
        print("########################################################")
        #events.bind('model.file.save.after', 'create_docker_job', _launchDockerJob)
        events.bind('jobs.status.validate', 'my_plugin', validateJobStatus)
        pass

