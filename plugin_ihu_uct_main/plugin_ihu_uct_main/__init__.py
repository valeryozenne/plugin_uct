from girder import plugin
from girder import events

## Girder model import.

# NOT USED
from girder.api import access
from girder.api.rest import Resource, RestException, loadmodel
from girder.plugin import getPlugin, GirderPlugin
from girder.models.user import User
from girder.models.group import Group
from girder.models.model_base import Model
from girder.models.upload import Upload
from girder.models.token import Token
from girder.utility.progress import ProgressContext
from girder.api.describe import Description, autoDescribeRoute, describeRoute
from girder.models.assetstore import Assetstore
from girder_worker.utils import JobManager
from girder_jobs import Job
from girder_client import GirderClient
from girder_jobs.constants import JobStatus
from girder_worker_utils import types
from girder.constants import TokenScope
from girder.api.rest import boundHandler
from girder_worker_utils.decorators import argument

# USED
from girder.constants import AccessType
from girder.models.item import Item
from girder.models.file import File
from girder.models.folder import Folder 
from girder.models.collection import Collection
from girder import events
from girder_worker.app import app
from girder.api.rest import getCurrentUser

## Custom import.
from plugin_ihu_uct_main.Tasks.Task1_img_conversion import call_girder_worker_convert_images_to_zarr, call_girder_worker_convert_images_to_nii
from gwexample.analyses.tasks import fibonacci_email, fibonacci

from plugin_test_pfa import call_girder_worker_progress
## Other import related to standard python.
import json
import os
import glob
import numpy as np

#######################


def call_girder_worker_fibonacci_email(number, filename, user_fullname, user_email):
   token = Token().createToken(user=getCurrentUser()) 
   async_result = fibonacci_email.delay(number, 
    filename=filename, 
    user_fullname=user_fullname, 
    user_email=user_email,
    girder_job_title='Fibonacci Email Job Perso with number'+ str(number),
  	girder_job_type='my_fibo_type',
  	girder_job_public=True,
    girder_client_token=token['_id']
	)

   return async_result.job

def call_girder_worker_fibonacci(number, filename, user_fullname, user_email):
   token = Token().createToken(user=getCurrentUser()) 
   async_result = fibonacci.delay(number,
    girder_job_title='Fibonacci Status Job Perso with number'+ str(number),
  	girder_job_type='my_fibo_type',
  	girder_job_public=True,
    girder_client_token=token['_id']
	)

   return async_result.job

def check_file_exist(file):
    '''
    Raises an error if the given file does not exist.
    '''
    if not (os.path.isfile(file)):
        print('file ',file,' doesn t exist')   
        raise ValueError("Error folder", file)
    
def check_folder_exist(folder):
    '''
    Raises an error if the given folder does not exist.
    '''
    if not (os.path.isdir(folder)):
        print('folder ',folder,' doesn t exist')   
        raise ValueError("Error folder", folder)
        
def create_folder(folder):
    '''
    Creates the given folder if it does not exist.
    '''
    if not (os.path.isdir(folder)):
        os.mkdir(folder)
    
def is_json_key_present(json, key):
    '''
    Returns True if key is present, otherwise an exception is raised up.
    '''
    try:
        buf = json[key]
    except KeyError:
        raise ValueError("No target in given data", key)
    return True

def fix_bordel_with_list_and_dict(sub_list_of_json_block):  
    '''
    TODO
    '''  
    len_sub = len(sub_list_of_json_block)
    d4 = dict(sub_list_of_json_block[0])
    for ii in range (1,len_sub):
      d4.update(sub_list_of_json_block[ii])  
  
    d5 = []
    d5.append(d4)  
    return d5

def read_log_file_and_save_as_json(filename, output_folder):
    '''
    TODO
    '''
    substring = '='
    num = 0
    num_sub = 0
    list_of_json_block = []
    list_of_json_name = []

    with open(filename, 'r') as infile:

    # Variable for building our JSON block
        
        for line in infile:

            # Add the line to our JSON block
            num += 1
            line = line.rstrip("\n")
        
            if substring in line:
                x = line.split("=")
                entry = {x[0]:x[1]} 
                list_of_json_block[num_sub-1].append(entry)
            else:
                json_block = [] 
                name = line[1:len(line)-1]
                list_of_json_name.append(name)
                list_of_json_block.append(json_block)
                num_sub += 1        

    # fix issue with dict and list

        for jj in range(0,num_sub):
          d5 = fix_bordel_with_list_and_dict(list_of_json_block[jj])
          new_data = {list_of_json_name[jj]: d5 }
          filename_out = 'uCT_'+list_of_json_name[jj]+'.json'
          filename_out = filename_out.replace(" ", "_")
          print(output_folder+'/'+filename_out)
          with open(output_folder+'/'+filename_out, "w") as file:
            json.dump(new_data, file)

    return list_of_json_block        

def get_spacing(list_of_json_block):
    '''
    TODO
    '''
    # fonction pour récupérer le spacing
    spacing=0
    Reconstruction=list_of_json_block[3]
    for it in Reconstruction:
      pairs = it. items()
      for key, value in pairs: 
         if ('Pixel' in key):
           print(key, value)
           spacing=value
    return spacing  

def upload_metadata_from_json(list_of_json_block, acquisitionItemDocument):
    '''
    Adds metadata 
    '''
    metadata = acquisitionItemDocument['meta']
    # fill all information 
    print('-------------')
    for tt in range(0, len(list_of_json_block)):
        lala = list_of_json_block[tt]

        for ll in range(0,len(lala)):  
            mini_dict = lala[ll]
            pairs = mini_dict.items()
            for key, value in pairs: 
                if ('.' in key):
                    pass
                else:
                    lolo = key.replace(".", "-")

                if key in metadata:
                    pass
                else:
                    if ('.' in lolo):
                        pass
                    else:
                        print(lolo, value)
                        meta_is_ok=Item().setMetadata( acquisitionItemDocument, {lolo:value}, allowNull=True)         


def extract_the_log_information(json_dictionary, event):
    '''
    Reads the 'filename' mail template.
    find the log file 
    read and parse the log file
    convert to json
    save it
    upload the metadata
    '''
    print('################# ###')
    print('extract_the_log_information')
    print('####################')


    filename = event.info['name']
    user_fullname = getCurrentUser()['firstName'] + " " + getCurrentUser()['lastName']
    user_email = getCurrentUser()['email']


    #folder_json_dictionarybase_uct='/home/bully/Desktop/GirderEcosystem/Girder_MicroCT/' # CHANGE THIS
    folder_json_dictionarybase_uct='/home/valeryozenne/mount/MicroCT/' # CHANGE THIS

    check_folder_exist(folder_json_dictionarybase_uct)
    name_project = json_dictionary['project-date']+'_'+ json_dictionary['project-id']+'_'+ json_dictionary['project-name'];
    name_sample = json_dictionary['sample-date']+'_'+ json_dictionary['sample-id']+'_'+ json_dictionary['sample-name'];   
    bruker_name = json_dictionary['bruker-name']

    folder_project = folder_json_dictionarybase_uct+name_project
    folder_sample = folder_json_dictionarybase_uct+name_project+"/"+name_sample
    folder_1_Rec_Data = folder_sample + '/1_Rec_Data'
    folder_2_Nii_Conversion= folder_sample + '/Task1_Nii_Conversion'
    folder_3_Zarr_Conversion = folder_sample +'/Task1_Zarr_Conversion'
    
    check_folder_exist(folder_project)
    check_folder_exist(folder_sample)  
    check_folder_exist(folder_1_Rec_Data)
    create_folder(folder_2_Nii_Conversion)
    create_folder(folder_3_Zarr_Conversion)

    # this should be define somewhere

    #collection_id='63ff9ae424d9b732fe930362'   # CHANGE THIS
    collection_id='619656b5dce91612bb7256dd'
    collectionDocument = Collection().load(collection_id, level=AccessType.WRITE,force=True)
    creatorId = event.info['creatorId']
    creator = {'_id':creatorId}
    
    projectFolderDocument = Folder().createFolder( collectionDocument, name_project, parentType='collection',reuseExisting=True, public=True, creator=None )
    sampleFolderDocument = Folder().createFolder( projectFolderDocument, name_sample, parentType='folder',reuseExisting=True, public=True, creator=None )
   
    # on n'est pas obligé de créer un item
    # on peut mettre les metadata dans le dossier
    acquisitionItemDocument = Item().createItem(name='log_from_rec_'+bruker_name, creator=creator, folder=sampleFolderDocument, reuseExisting=True)
    

    log_file = folder_1_Rec_Data+'/'+bruker_name+'__rec.log'
    check_file_exist(log_file)
    list_of_json_block = read_log_file_and_save_as_json(log_file, folder_1_Rec_Data)
    spacing = get_spacing(list_of_json_block)  
   
    upload_metadata_from_json(list_of_json_block, acquisitionItemDocument) 

    myListOfExtension=[]

    liste_bmp = glob.glob(folder_1_Rec_Data+'/'+ bruker_name +'__rec0000????.bmp')
    print(len(liste_bmp))
    myListOfExtension.append(len(liste_bmp))
    liste_tif = glob.glob(folder_1_Rec_Data+'/'+ bruker_name +'__rec0000????.tif')
    print(len(liste_tif))
    myListOfExtension.append(len(liste_tif))
    liste_png = glob.glob(folder_1_Rec_Data+'/'+ bruker_name +'__rec0000????.png')
    print(len(liste_png))
    myListOfExtension.append(len(liste_png))
    
    arr = np.array([len(liste_bmp), len(liste_tif), len(liste_png)])
    tri = np.argsort(arr)
    if (tri[-1] == 2):
       extension='.png' 
       print('extension is png')  
    elif(tri[-1] == 1):
        extension ='.tif'
        print('extension is tiff')  
    elif(tri[-1] == 0):
        extension = '.bmp'
        print('extension is bmp')  
    else:   
      print("Error extension tri vaut ", tri[-1])   
      raise ValueError("Error extension tri vaut ", tri[-1])

    
    nii_job = call_girder_worker_convert_images_to_nii(folder_1_Rec_Data, folder_2_Nii_Conversion,bruker_name, extension, filename, user_fullname, user_email)
    zarr_job = call_girder_worker_convert_images_to_zarr(folder_1_Rec_Data, folder_3_Zarr_Conversion,bruker_name, extension, filename, user_fullname, user_email)
    
def count_bmp_images_in_folder(folder_path):
    '''
    Returns the number of bmp images in the given folder.
    '''
    img_count = 0
    for _, _, files in os.walk(folder_path, topdown=False):
        for name in files:
            _, extension = os.path.splitext(name)
            if extension.lower() == '.bmp':
                img_count += 1

    return img_count

def read_json_file(file_id):
    '''
    Reads json file.
    '''

    json_file = File().load(file_id, force=True)
    with File().open(json_file) as f:
        json_data = json.load(f)

    return json_data

def json_insertion_scenario(file_id, event):
    '''
    Launches job action with the give file. 
    '''
    json_data = read_json_file(file_id)
    print(json_data)

    if is_json_key_present(json_data, 'disque'):
        path_to_drive = json_data['disque']

        print("Count images in the disc folder:", path_to_drive)
        #print("Number of images in the folder:", count_bmp_images_in_folder(path_to_drive))
        extract_the_log_information(json_data, event)
    
@app.task(bind=True)
def _launchActionConversion(self, event):
    '''
    Job action launching function.
    '''
    print('================ Lanching the Job Conversion ===================')   

    file_id = event.info['_id'] # Retrieving inserted file id.
    
    if event.info['mimeType'] == "application/json":
        # Inserted file is a json file.
        print("A json has been inserted \n")
        json_insertion_scenario(file_id, event)
            

    #self.update_state(state="PROGRESS", meta={'progress': 50})
    print('================ End of the Job ===================')   


@app.task(bind=True)
def _launchActionComputeTensor(self, event):
    '''
    Job action launching function.
    '''
    print('================ Lanching the Job ComputeTensor ===================')   

    item_id = event.info['_id'] # Retrieving inserted file id.
    print(item_id)    
    print('================ End of the Job ComputeTensor ===================')   


@app.task(bind=True)
def _launchActionComputeVectors(self, event):
    '''
    Job action launching function.
    '''
    print('================ Lanching the Job ComputeVectors ===================')   

    item_id = event.info['_id'] # Retrieving inserted file id.
    print(item_id)    
    print('================ End of the Job ComputeVectors ===================')   

@app.task(bind=True)
def _launchActionComputeMetrics(self, event):
    '''
    Job action launching function.
    '''
    print('================ Lanching the Job ComputeMetrics ===================')   

    item_id = event.info['_id'] # Retrieving inserted file id.
    print(item_id)    
    print('================ End of the Job ComputeMetrics ===================')  


@app.task(bind=True)
def _launchActionExamples(self, event):
    '''
    Job action launching function.
    '''
    print('================ Lanching the Job Examples ===================')   

    item_id = event.info['_id'] # Retrieving inserted file id.
    filename= event.info['name']
    print(item_id) 
 
    user_fullname = getCurrentUser()['firstName'] + " " + getCurrentUser()['lastName']
    user_email = getCurrentUser()['email']   
    
    number=20
    call_girder_worker_fibonacci(number, filename, user_fullname, user_email)

    number =20    
    job=call_girder_worker_progress(number,filename, user_fullname,user_email)
    print(job)
    number =15    
    job=call_girder_worker_progress(number,filename, user_fullname,user_email)
    print(job)

    print('================ End of the Job Examples ===================')     


@app.task(bind=True)
def _launchActionReConversion(self, event):
    '''
    Job action launching function.
    '''
    print('================ Lanching the Job ComputeTensor ===================')   

    file_id = event.info['_id'] # Retrieving inserted file id.
    print(file_id)
    if event.info['mimeType'] == "application/json":
        # Inserted file is a json file.
        print("A json has been inserted \n")
    else:
        print("A json has not been inserted \n")  
    #    json_insertion_scenario(file_id, event)            

    #self.update_state(state="PROGRESS", meta={'progress': 50})
    print('================ End of the Job ComputeTensor ===================')   



class GirderPlugin(plugin.GirderPlugin):  
    DISPLAY_NAME = 'plugin_ihu_uct_main'
    CLIENT_SOURCE_PATH = 'web_client'

    def load(self, info):
        # Binding file saving event to a task.
        events.bind('model.file.save.after', 'Upload Run job', _launchActionConversion) 
        events.bind('Run job fibonacci and progress', 'Run job fibonacci and progress', _launchActionExamples)
        #events.bind('Run job computeTensor', 'Run job computeTensor', _launchActionComputeTensor)
        #events.bind('Run job computeVectors', 'Run job computeVectors', _launchActionComputeVectors)
        #events.bind('Run job computeMetrics', 'Run job computeMetrics', _launchActionComputeMetrics)
        pass
