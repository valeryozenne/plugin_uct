from girder import plugin
from girder import events

## girder model import
from girder.api import access
from girder.api.describe import Description, describeRoute
from girder.api.rest import Resource, RestException, loadmodel
from girder.constants import AccessType, TokenScope
from girder.plugin import getPlugin, GirderPlugin
from girder.models.item import Item
from girder.models.user import User
from girder.models.file import File
from girder.models.group import Group
from girder.models.model_base import Model
from girder.models.upload import Upload
from girder.models.folder import Folder 
from girder.models.collection import Collection
from girder.models.token import Token
from girder import events
from girder.api import access

from girder.constants import AccessType, TokenScope
from girder.api.rest import boundHandler, getCurrentUser
from girder.api.describe import Description, autoDescribeRoute
from girder.api.rest import Resource
from girder.models.assetstore import Assetstore


## other import related to standard python
import json
import os
import glob
import numpy as np

# list of function that should be moved in other python_file.py for clearity

def check_file_exist(file):
   if not (os.path.isfile(file)):
    print('file ',file,' doesn t exist')   
    raise ValueError("Error folder", file)
    
def check_folder_exist(folder):
   if not (os.path.isdir(folder)):
    print('folder ',folder,' doesn t exist')   
    raise ValueError("Error folder", folder)
    
def check_folder_exist_or_create_it(folder):
   if not (os.path.isdir(folder)):
      os.mkdir(folder)
    
def is_json_key_present(json, key):
    try:
        buf = json[key]
    except KeyError:
        raise ValueError("No target in given data", key)
    return True


def fix_bordel_with_list_and_dict(sub_list_of_json_block):    
    len_sub=len(sub_list_of_json_block)
    d4=dict(sub_list_of_json_block[0])
    for ii in range (1,len_sub):
      d4.update(sub_list_of_json_block[ii])  
  
    d5=[]
    d5.append(d4)  
    return d5

def read_log_file_and_save_as_json(filename, output_folder):
    
    substring='='
    num=0
    num_sub=0
    list_of_json_block=[]
    list_of_json_name=[]

    with open(filename, 'r') as infile:

    # Variable for building our JSON block
        
        for line in infile:

            # Add the line to our JSON block
            num+=1
            line=line.rstrip("\n")
        
            if substring in line:
                #print("Found!")
                #print('coucou')
                x = line.split("=")
                #print(x)
                entry = {x[0]:x[1]} 
                #print(entry)
                #new_entry= {'people': x[0] }
                list_of_json_block[num_sub-1].append(entry)
                #list_of_json_block[num_sub-1].append([x[0], x[1]])
            else:
            
                #print("Not found!")
                #print(line)
                #print(num,num_sub)
                json_block = [] 
                name=line[1:len(line)-1]
                list_of_json_name.append(name)
                list_of_json_block.append(json_block)
                num_sub+=1        

    # fix issue with dict and list

        for jj in range(0,num_sub):
          d5=fix_bordel_with_list_and_dict(list_of_json_block[jj])
          new_data= {list_of_json_name[jj]: d5 }
          #print(json.dumps(new_data, sort_keys=True, indent=4))
          filename_out='uCT_'+list_of_json_name[jj]+'.json'
          filename_out=filename_out.replace(" ", "_")
          print(output_folder+'/'+filename_out)
          with open(output_folder+'/'+filename_out, "w") as file:
            json.dump(new_data, file)

    return list_of_json_block        


def get_spacing(list_of_json_block):
    # fonction pour récupérer le spacing
    spacing=0
    Reconstruction=list_of_json_block[3]
    for it in Reconstruction:
      #print(it)
      pairs = it. items()
      for key, value in pairs: 
         if ('Pixel' in key):
           print(key, value)
           spacing=value
    return spacing  


def upload_metadata_from_json(list_of_json_block,acquisitionItemDocument):

    metadata=acquisitionItemDocument['meta']
    # fill all information 
    print('-------------')
    for tt in range(0,len(list_of_json_block)):
        #print(tt)
        lala=list_of_json_block[tt]
        for ll in range(0,len(lala)):  
          mini_dict=lala[ll]
          pairs = mini_dict.items()
          for key, value in pairs: 
                if ('.' in key):
                        pass
                else:
                    lolo = key.replace(".", "-")

                if key in metadata:
                        pass
                        #print("baah")
                        #print(lolo, value)
                else:
                        #print("boo")
                        #print(lolo, value)
                        if ('.' in lolo):
                            pass
                        else:
                            print(lolo, value)
                            meta_is_ok=Item().setMetadata( acquisitionItemDocument, {lolo:value}, allowNull=True)         




def call_function_rec_conversion(json_dictionary, event):
    pass

def create_the_directories():
    pass 

def extract_the_log_information(json_dictionary, event):
    
    # function do too many things, it has to be splitted
    # check that the physical folder (where are the data) exists
    # find the log file 
    # read and parse the log file
    # convert to json
    # save it
    # upload the metadata

    print('####################')
    print('extract_the_log_information')
    print('####################')

    if (json_dictionary['disque']!='Imagerie2'):
       raise ValueError("Error")
    else:
       pass
      # it should define in the json file

    folder_json_dictionarybase_uct='/home/valeryozenne/mount/Imagerie/For_Valery/Girder_MicroCT/' 

    check_folder_exist(folder_json_dictionarybase_uct)
    name_project=json_dictionary['project-date']+'_'+ json_dictionary['project-id']+'_'+ json_dictionary['project-name'];
    name_sample=json_dictionary['sample-date']+'_'+ json_dictionary['sample-id']+'_'+ json_dictionary['sample-name'];   
    bruker_name=json_dictionary['bruker-name']

    folder_project=folder_json_dictionarybase_uct+name_project
    folder_sample= folder_json_dictionarybase_uct+name_project+"/"+name_sample
    folder_1_Rec_Data= folder_sample + '/1_Rec_Data'
    folder_2_Nii_Converted= folder_sample + '/2_Nii_Converted'
    
    check_folder_exist(folder_project)
    check_folder_exist(folder_sample)  
    check_folder_exist(folder_1_Rec_Data)
    check_folder_exist_or_create_it(folder_2_Nii_Converted)

    # this should be define somewhere
    collection_id='619656b5dce91612bb7256dd'   
    collectionDocument = Collection().load(collection_id, level=AccessType.WRITE,force=True)
     
    creator=event.info['currentUser']
    #print(creator)
    projectFolderDocument = Folder().createFolder( collectionDocument, name_project, parentType='collection',reuseExisting=True, public=True, creator=creator )
    sampleFolderDocument = Folder().createFolder( projectFolderDocument, name_sample, parentType='folder',reuseExisting=True, public=True, creator=creator )
    
    sampleFolderDocument = Folder().createFolder( projectFolderDocument, 'titi', parentType='folder',reuseExisting=True, public=True, creator=creator )
    
    subFolderDocument = Folder().createFolder( sampleFolderDocument, 'tutu', parentType='folder',reuseExisting=True, public=True, creator=creator )
    
    acquisitionItemDocument = Item().createItem(name='log_titi', creator=creator, folder=sampleFolderDocument, reuseExisting=True)
    
    subacquisitionItemDocument = Item().createItem(name='log_titi', creator=creator, folder=subFolderDocument, reuseExisting=True)
    
    #id_item='6400cdc11430421cf8e56840'

    #item_dict = Item().load(id_item, level=AccessType.WRITE, force=True)

    meta_is_ok=Item().setMetadata( subacquisitionItemDocument, {"lolo":"47"}, allowNull=True)

    # on n'est pas obligé de créer un item
    # on peut mettre les metadata dans le dossier
    acquisitionItemDocument = Item().createItem(name='log_from_rec_'+bruker_name, creator=creator, folder=sampleFolderDocument, reuseExisting=True)
    
    #print(json_dictionary)
    log_file=folder_1_Rec_Data+'/'+bruker_name+'__rec.log'
    check_file_exist(log_file)
    list_of_json_block=read_log_file_and_save_as_json(log_file, folder_1_Rec_Data)
    spacing=get_spacing(list_of_json_block)  
   
    upload_metadata_from_json(list_of_json_block,acquisitionItemDocument) 

    myListOfExtension=[]

    liste_bmp=glob.glob(folder_1_Rec_Data+'/'+ bruker_name +'__rec0000????.bmp')
    print(len(liste_bmp))
    myListOfExtension.append(len(liste_bmp))
    liste_tif=glob.glob(folder_1_Rec_Data+'/'+ bruker_name +'__rec0000????.tif')
    print(len(liste_tif))
    myListOfExtension.append(len(liste_tif))
    liste_png=glob.glob(folder_1_Rec_Data+'/'+ bruker_name +'__rec0000????.png')
    print(len(liste_png))
    myListOfExtension.append(len(liste_png))
    
    arr = np.array([len(liste_bmp), len(liste_tif), len(liste_png)])
    tri=np.argsort(arr)
    if (tri[-1]==2):
       extension='.png' 
       print('extension is png')  
    elif(tri[-1]==1):
        extension='.tif'
        print('extension is tiff')  
    elif(tri[-1]==0):
        extension='.bmp'
        print('extension is bmp')  
    else:   
      print("Error extension tri vaut ", tri[-1])   
      raise ValueError("Error extension tri vaut ", tri[-1])

    #call_girder_worker_conversion_rec_to_nii(folder_1_Rec_Data, folder_2_Nii_Converted,bruker_name, extension, creator) 
    #creator=event.info['currentUser']
    #print(creator)

def read_and_check_that_the_format_of_json_file_is_ok(event):

    print(event.info)
    file = event.info['file']
   
    filename=file['name']

    # open the file
    json_file = File().open(file)
    # load the key valye
    json_dictionary = json.load(json_file)

    # check that the key are ok
    is_json_key_present(json_dictionary,'task-name')    
    is_json_key_present(json_dictionary,'disque')      
    is_json_key_present(json_dictionary,'project-date')       
    is_json_key_present(json_dictionary,'project-id')     
    is_json_key_present(json_dictionary,'project-name')  
    is_json_key_present(json_dictionary,'sample-date')       
    is_json_key_present(json_dictionary,'sample-id')     
    is_json_key_present(json_dictionary,'sample-name')    
    is_json_key_present(json_dictionary,'operation')  
    is_json_key_present(json_dictionary,'bruker-name')
    is_json_key_present(json_dictionary,'level')   
    is_json_key_present(json_dictionary,'rho')  

    # if something wrong
    # do something
    # 
    # otherwise continue    
    #
    spacing=extract_the_log_information(json_dictionary, event)  

    # the json file include a line which define the operation
    # this has to be removed and remplaced by a clic in the interface
    operation=json_dictionary['operation']

    #if (json_dictionary['operation']=='Rec_Conversion'):
    #elif (json_dictionary['operation']=='STI'):        
    #else:
    #    raise ValueError("Error", json_dictionary['operation']) 
  
def identify_the_task_to_be_done(event, filename):

    # if the file is a json , that's ok

    if ("task" in filename) and ("json" in filename):
      
      print('####################')
      print('d')
      print('####################')
      read_and_check_that_the_format_of_json_file_is_ok(event)

    else:
        print('####################')
        print('not going into the plugin') 
        print('####################') 

def _handler_data_process(event):

    ##
    #once a file is upload we gonna do some tasks
    # we will use the name and format of the file to identify the file

    info = event.info
    file = info['file']
    filename=file['name']
    reference = event.info.get('reference', None)

    identify_the_task_to_be_done(event, filename)

    print('####################')
    print(' plugin µct fin du handler ') 
    print('####################')



class GirderPlugin(plugin.GirderPlugin):
    DISPLAY_NAME = 'plugin_uct'
    CLIENT_SOURCE_PATH = 'web_client'

    def load(self, info):
        # add plugin loading logic here

        print('####################')
        print(' plugin µct start du handler ') 
        print('####################')
        # please check the doc
        # basically the line below trigger the plugin if a file is uploaded
        
        # be careful for some reasons the data process events cannot send jobs..
        # events.bind('data.process', 'my_first_process', _handler_data_process) 
        # while the events bind model can send jobs
        # events.bind('model.file.save.after', 'lance une action', _handler)       
        pass
