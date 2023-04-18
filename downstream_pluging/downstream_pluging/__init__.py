from girder import plugin
from girder import events

from girder_jobs.constants import JobStatus
from girder_worker_utils.decorators import argument
from girder_worker_utils import types
from string import Template
from girder.utility import mail_utils
from girder.models.user import User

import girder.api.v1.user as user_api
from girder.models.user import User
from girder.exceptions import RestException
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
@argument('user_fullname', types.String, min=1, max=1)
@argument('user_email', types.String, min=1, max=1)
@argument('template_name', types.String, min=1, max=1)
def mail_sender(job_name, start_hour, processed_file, user_fullname, user_email, template_name):
    '''
    Sends a mail to the current user running the job with some log information:
    - the user fullname;
    - the job name;
    - the job launching start hour;
    - the processed file name;
    - the user fullname;
    - the user email;
    - the corresponding mail template.
    '''
    
    if user_email is not None and mail_utils.validateEmailAddress(user_email):
        print('####################')
        print('mail_sender')
        print('####################')
        message_template = read_mail_template(template_name)
        message = message_template.substitute(PERSON_NAME=user_fullname, JOB_NAME=job_name, START_HOUR=start_hour, PROCESSED_FILE=processed_file)
        mail_utils.sendMail(subject='My mail from girder', text=message, to=user_email)
    else:
        print("send_mail_error")

def get_mail_template(status):
  if (status == JobStatus.SUCCESS):
    return "success_template.txt"
  elif (status == JobStatus.ERROR):
    return "error_template.txt"
  elif (status == JobStatus.CANCELED):  
    return "canceled_template.txt" 
  else:
     return "default_template.txt"

def validate_job_status(event):
    event_job = event.info['job']
    current_status = event_job['status']
    args = event_job['kwargs']

    print("this is the progress:", current_status)

    if (current_status == 1234):
        event.preventDefault().addResponse(True)
        print('event.info == 1234')

    if (current_status == JobStatus.INACTIVE):
      print('event.info == INACTIVE (0)')
    elif (current_status == JobStatus.QUEUED):
      print('event.info == QUEUED (1)')   
    elif (current_status == JobStatus.RUNNING):
      print('event.info == RUNNING (2) ')
    elif (current_status == JobStatus.SUCCESS or current_status == JobStatus.ERROR or current_status == JobStatus.CANCELED):
      job_name = event_job['title']
      created_at = event_job['created'].strftime("%H:%M:%S")
      filename = args['filename']
      user_fullname = args['user_fullname']
      user_email = args['user_email']
      mail_template = get_mail_template(current_status)

      mail_sender(job_name, created_at, filename, user_fullname, user_email, mail_template)
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
        # events.bind('jobs.status.validate', 'my_plugin', validateJobStatus)
        events.bind('jobs.job.update.after', "update after", validate_job_status)
        # events.bind('jobs.job.update', "update", validateJobStatus)
        pass
    