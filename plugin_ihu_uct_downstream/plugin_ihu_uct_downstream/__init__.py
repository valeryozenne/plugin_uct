from girder import plugin
from girder import events

from girder_jobs.constants import JobStatus
from girder_worker_utils.decorators import argument
from girder_worker_utils import types
from string import Template
from girder.utility import mail_utils
from girder.settings import SettingKey

import os
import json
#######################

def read_mail_template(filename):
    '''
    Reads the 'filename' mail template.
    '''
    with open(filename, 'r', encoding='utf-8') as template_file:
        template_file_content = template_file.read()
    return Template(template_file_content)

#@argument('job_name', types.String, min=1, max=1)
#@argument('user_email', types.String, min=1, max=1)
#@argument('subject_email', types.String, min=1, max=1)
#@argument('processed_file', types.String, min=1, max=1)
#@argument('user_fullname', types.String, min=1, max=1)


@argument('template_name', types.String, min=1, max=1)
def mail_sender(event_job,  template_name):
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
    print('####################')
    print('mail_sender')
    print('####################')

    id=event_job['_id']
    job_name = event_job['title']
    start_hour = event_job['created'].strftime("%H:%M:%S")
    end_hour = event_job['updated'].strftime("%H:%M:%S")
    job_arguments=event_job['args']

    print("job_arguments", job_name)
    print(len(job_arguments))
    print("job_arguments", job_arguments)
    ####
    bruker_name=job_arguments[2]
     
    processed_file = job_arguments[len(job_arguments)-3]
    user_fullname = job_arguments[len(job_arguments)-2]
    user_email = job_arguments[len(job_arguments)-1]
    
    print("user_email", user_email)

    dict_split_path=job_arguments[0].split('/')
    if dict_split_path[len(dict_split_path)-1]=='1_Rec_Data':
       print("this is the conversion operation")
    ####
    subject_email="MilleFeuilles Notification - SUCCESS - " + bruker_name   
    
    try:
      if user_email is None or not mail_utils.validateEmailAddress(user_email):
        raise
      message_template = read_mail_template(template_name)
      message = message_template.substitute(PERSON_NAME=user_fullname, JOB_NAME=job_name, START_HOUR=start_hour, END_HOUR=end_hour, PROCESSED_FILE=processed_file)
      mail_utils.sendMail(subject=subject_email, text=message, to=user_email)
    except:
      print("send_mail_error")

def get_mail_template(status):
  '''
  Returns mail template corresponding to the given status.
  '''
  if (status == JobStatus.SUCCESS):
    return "success_template.txt"
  elif (status == JobStatus.ERROR):
    return "error_template.txt"
  elif (status == JobStatus.CANCELED):  
    return "canceled_template.txt" 
  else:
     return "default_template.txt"

def validate_job_status(event):
    '''
    Retrieves and handles job status actions.
    '''
    event_job = event.info['job']
    job_name = event_job['title']
    job_name_lower_cases = job_name.lower()

    if "status" in job_name_lower_cases:
        print(job_name_lower_cases , " include status")
         
        current_status = event_job['status']
        args = event_job['args']
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
          #id=event_job['_id']
          #job_name = event_job['title']
          #created_at = event_job['created'].strftime("%H:%M:%S")
          #updated_at = event_job['updated'].strftime("%H:%M:%S")
          #filename = args[len(args)-3]
          #user_fullname = args[len(args)-2]
          #user_email = args[len(args)-1]
          #bruker_name=event_job['args'][2]         

          if "email" in job_name_lower_cases:
            print(job_name_lower_cases , " include email")
            mail_template = get_mail_template(current_status)
            mail_sender(event_job, mail_template)
          else:
            print(job_name_lower_cases , " do not include email") 

        else:
            print('event.info == X') 
    else:
        print(job_name_lower_cases , " do not include status")      

@argument('json_filename', types.String, min=1, max=1)
def read_json_file_as_secret(json_filename) -> dict:
    '''
    Reads data corresponding to the given json file as a secret.
    '''
    filename = os.path.join(json_filename)
    try:
        with open(filename, mode='r') as f:
            return json.loads(f.read())
    except FileNotFoundError:
        return {}

def set_settings():
    '''
    Sets SMTP webmail server configuration information.
    '''
    from girder.models.setting import Setting
    setting = Setting()
    
    secrets = read_json_file_as_secret('settings.json')
    setting.set(SettingKey.SMTP_ENCRYPTION, secrets["SMTP_ENCRYPTION"])
    setting.set(SettingKey.SMTP_HOST, secrets["SMTP_HOST"])
    setting.set(SettingKey.SMTP_PASSWORD, secrets["SMTP_PASSWORD"])
    setting.set(SettingKey.SMTP_PORT, secrets["SMTP_PORT"])
    setting.set(SettingKey.SMTP_USERNAME, secrets["SMTP_USERNAME"])

class GirderPlugin(plugin.GirderPlugin):
    DISPLAY_NAME = 'plugin_ihu_uct_downstream'  
    CLIENT_SOURCE_PATH = 'web_client'
   
    # downstream plugin
    def load(self, info):
        set_settings()
        print('####################')
        print(' plugin downstream start du handler ') 
        print('####################')

        events.bind('jobs.job.update.after', "update after", validate_job_status)
        pass
    