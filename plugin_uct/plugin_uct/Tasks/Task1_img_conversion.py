import os
import numpy as np
import dask.array as da
import nibabel as nib
import time
import glob
import zarr
from skimage import io
from girder_worker.app import app
from girder_jobs.models.job import Job
from girder.constants import AccessType, TokenScope
from girder_jobs import Job
from girder_jobs.constants import JobStatus
from girder.models.token import Token
from girder.api.rest import getCurrentUser
from celery.result import AsyncResult
from girder_worker.task import Task
import requests


# @app.task
# def task1_convert_rec_to_zarr(job,folder_path, save_folder_path):
    
#     job = Job().updateJob(
#             job, log='Started Zarr conversion\n',
#             status=JobStatus.RUNNING,
#             progressCurrent=0,
#             progressTotal=100
#         )

#     img_arrays = []
#     for _, _, files in os.walk(folder_path, topdown=False):
#         for name in files:
#             _, extension = os.path.splitext(name)
#             if extension.lower() == '.bmp' or extension.lower() == '.tif':
#                 img_path = os.path.join(folder_path, name)
#                 img = imageio.imread(img_path)
#                 img_arrays.append(da.from_array(img))
#     concatenated_imgs = da.concatenate(img_arrays, axis=0)
#     # save_folder_path = os.path.join(save_folder_path, 'Task1')
#     os.makedirs(save_folder_path, exist_ok=True)
#     da.to_zarr(concatenated_imgs, os.path.join(save_folder_path, 'concatenated_images.zarr'))
#     job = Job().updateJob(
#             job, log='Finished Zarr conversion\n',
#             status=JobStatus.RUNNING,
#             progressCurrent=0,
#             progressTotal=100
#         )
    
#     return job

# @app.task
# def task1_convert_images_to_nii(folder_path, save_folder_path):
#     img_arrays = []
#     for _, _, files in os.walk(folder_path, topdown=False):
#         for name in files:
#             _, extension = os.path.splitext(name)
#             if extension.lower() == '.bmp' or extension.lower() == '.tif':
#                 img_path = os.path.join(folder_path, name)
#                 img = imageio.imread(img_path)
#                 img_arrays.append(da.from_array(img))
#     concatenated_imgs = da.concatenate(img_arrays, axis=0)
#     # save_folder_path = os.path.join(save_folder_path, 'Task1')
    
#     nii_img = nib.Nifti1Image(concatenated_imgs.compute(), np.eye(4))
#     nib.save(nii_img, os.path.join(save_folder_path, 'concatenated_images.nii.gz'))
    
#     return concatenated_imgs




#job_manager = app.job_manager


@app.task(bind=True)
def task1_convert_rec_to_nii(self,input_dir, output_dir, bruker_name, extension, filename, user_fullname, user_email):
    self.job_manager.updateProgress(total=10, current=0)

    print('Starting the job')
    self.job_manager.updateProgress(total=10, current=1)

    file_pattern = os.path.join(input_dir, bruker_name + '__rec0000????' + extension)
    file_list = glob.glob(file_pattern, recursive=False)
    print(f'Found {len(file_list)} files matching pattern {file_pattern}')
    self.job_manager.updateProgress(total=10, current=2)

    # Check for truncated files and replace them with the previous file
    num_truncated_files = 0
    for i, file_path in enumerate(file_list):
        print(f'Trying to read file {i}: {file_path}')
        try:
            im = io.imread(file_path)
        except ValueError:
            if i == 0:
                raise ValueError("Error: Truncated file is the first one")
            else:
                file_list[i] = file_list[i-1]
                num_truncated_files += 1
                print("Warning: Using the previous image for this file")

    if num_truncated_files > 0:
        print(f"Detected {num_truncated_files} truncated files")
    self.job_manager.updateProgress(total=10, current=5)

    # Load images and concatenate them into a 3D array
    t = time.time()
    im_collection = io.imread_collection(file_list)
    im_3d = im_collection.concatenate()
    elapsed = time.time() - t
    print(f"Loaded {len(im_collection)} files in {elapsed:.2f} seconds")
    
    self.job_manager.updateProgress(total=10, current=8)
    # Create NIfTI image and save to disk
    try:
        t = time.time()
        img = nib.Nifti1Image(im_3d, affine=np.eye(4))
        img.to_filename(os.path.join(output_dir, 'uct_rec.nii.gz'))
        elapsed = time.time() - t
        print(f"Saved NIfTI image in {elapsed:.2f} seconds")
        status = JobStatus.SUCCESS
    except Exception as e:
        print(f"Error saving NIfTI image: {e}")
        status = JobStatus.ERROR
    self.job_manager.updateProgress(total=10, current=9)
    print('Ending the job')
    return None


@app.task(bind=True)
def convert_rec_to_zarr(self, input_dir, output_dir, bruker_name, extension, filename, user_fullname, user_email):

    self.job_manager.updateProgress(total=10, current=0)
    print('Starting the job')
    print(f'Searching for files in {input_dir}/{bruker_name}__rec0000????{extension}')
    
    self.job_manager.updateProgress(total=10, current=2)
    # Find all image files
    file_pattern = os.path.join(input_dir, f'{bruker_name}__rec0000????{extension}')
    image_files = sorted(glob.glob(file_pattern))
    print(f'Found {len(image_files)} files')

    self.job_manager.updateProgress(total=10, current=4)
    # Check if image is truncated, if so use the previous image
    num_truncated_files = 0
    for i in range(len(image_files)):
        image_path = image_files[i]
        image_collection = io.imread_collection(image_path)
        print(f'Trying to read file {i}: {image_path}')
        try:
            _ = image_collection.concatenate()
        except ValueError:
            if i > 0:
                image_files[i] = image_files[i-1]
                num_truncated_files += 1
                print(f'Attention: using the same image twice. File {i} is truncated.')
            else:
                return None
    print(f'Found {num_truncated_files} truncated files')

    self.job_manager.updateProgress(total=10, current=6)
    # Concatenate images
    t_start = time.time()
    print('Concatenating images')
    image_collection = io.imread_collection(image_files)
    image_3d = image_collection.concatenate()
    elapsed_time = time.time() - t_start
    print(f'Finished concatenating images in {elapsed_time:.2f}s')
    t_start = time.time()
    print(f'Saving .zarr file to {output_dir}')
    os.makedirs(output_dir, exist_ok=True)
    try:
        zarr.save(output_dir, image_3d)
    except Exception as e:
        return None
    
    elapsed_time = time.time() - t_start
    print(f'Finished saving .zarr file in {elapsed_time:.2f}s')
    self.job_manager.updateProgress(total=10, current=9)
    return None

def call_girder_worker_convert_images_to_zarr(input_dir,output_dir,bruker_name,extension, filename, user_fullname, user_email):
    task_result = convert_rec_to_zarr.apply_async(args=(input_dir, output_dir, bruker_name, extension, filename, user_fullname, user_email),kwargs={},
	girder_job_title='Convert Images to zarr', countdown = 4)
    while not task_result.ready():
        time.sleep(5)

    if task_result.successful():
        print("Task completed successfully!")
    else:
        print("Task failed.")
    return task_result.successful() 



def call_girder_worker_convert_images_to_nii(input_dir,output_dir,bruker_name,extension, filename, user_fullname, user_email): 

    task_result = task1_convert_rec_to_nii.apply_async(args=(input_dir, output_dir, bruker_name, extension, filename, user_fullname, user_email),kwargs={},
	girder_job_title='Convert Images to nii', countdown=3)

    while not task_result.ready():
        time.sleep(5)

    if task_result.successful():
        print("Task completed successfully!")
    else:
        print("Task failed.")
    return task_result.successful()
