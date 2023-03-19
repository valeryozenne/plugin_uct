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






@app.task
def task1_convert_rec_to_nii(job,input_dir, output_dir, bruker_name, extension):
    
    print('Starting the job')
    
    job = Job().updateJob(
            job, log='Started Nii conversion\n',
            status=JobStatus.RUNNING,
            progressCurrent=0,
            progressTotal=100
        )
    
    file_pattern = os.path.join(input_dir, bruker_name + '__rec0000????' + extension)
    file_list = glob.glob(file_pattern, recursive=False)
    print(f'Found {len(file_list)} files matching pattern {file_pattern}')

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

    # Load images and concatenate them into a 3D array
    t = time.time()
    im_collection = io.imread_collection(file_list)
    im_3d = im_collection.concatenate()
    elapsed = time.time() - t
    print(f"Loaded {len(im_collection)} files in {elapsed:.2f} seconds")
    
    # Update progress and status
    job = Job().updateJob(
            job, log=f'Loaded {len(im_collection)} files in {elapsed:.2f} seconds\n',
            status=JobStatus.RUNNING,
            progressCurrent=20,
            progressTotal=100
        )

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

    print('Ending the job')
    job = Job().updateJob(
            job, log='Finished Nii conversion\n',
            status=status,
            progressCurrent=100,
            progressTotal=100
        )
    return job


@app.task
def convert_rec_to_zarr(job, input_dir, output_dir, bruker_name, extension):
    print('Starting the job')
    
    # Update job status to RUNNING
    job = Job().updateJob(
        job,
        log='Started Zarr conversion\n',
        status=JobStatus.RUNNING,
        progressCurrent=0,
        progressTotal=100
    )

    print(f'Searching for files in {input_dir}/{bruker_name}__rec0000????{extension}')
    
    # Find all image files
    file_pattern = os.path.join(input_dir, f'{bruker_name}__rec0000????{extension}')
    image_files = sorted(glob.glob(file_pattern))
    print(f'Found {len(image_files)} files')

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
                # Update job status to ERROR if the first file is truncated
                job = Job().updateJob(
                    job,
                    log=f'Error: The first file {image_path} is truncated.\n',
                    status=JobStatus.ERROR,
                    progressCurrent=0,
                    progressTotal=100
                )
                return job
    print(f'Found {num_truncated_files} truncated files')

    # Concatenate images
    t_start = time.time()
    print('Concatenating images')
    image_collection = io.imread_collection(image_files)
    image_3d = image_collection.concatenate()
    elapsed_time = time.time() - t_start
    print(f'Finished concatenating images in {elapsed_time:.2f}s')
    
    # Update progress to 40%
    job = Job().updateJob(
        job,
        log='40% of the job completed.\n',
        status=JobStatus.RUNNING,
        progressCurrent=40,
        progressTotal=100
    )

    # Save as .zarr
    t_start = time.time()
    print(f'Saving .zarr file to {output_dir}')
    os.makedirs(output_dir, exist_ok=True)
    try:
        zarr.save(output_dir, image_3d)
    except Exception as e:
        # Update job status to ERROR if there is an error while saving
        job = Job().updateJob(
            job,
            log=f'Error: {str(e)}\n',
            status=JobStatus.ERROR,
            progressCurrent=0,
            progressTotal=100
        )
        return job
    elapsed_time = time.time() - t_start
    print(f'Finished saving .zarr file in {elapsed_time:.2f}s')

    # Update progress to 100%
    job = Job().updateJob(
        job,
        log='Finished Zarr Conversion\n',
        status=JobStatus.SUCCESS,
        progressCurrent=100,
        progressTotal=100
    )
    
    return job

def call_girder_worker_convert_images_to_zarr(input_dir,output_dir,bruker_name,extension):
    
    zarr_job = Job().createLocalJob(
                module='plugin_uct.Tasks',
                function='task1_convert_rec_to_zarr',
                title='Convert Rec to zarr',
                type='conversion',
                public=False,
                asynchronous=True
            )
    zarr_job = convert_rec_to_zarr(zarr_job,input_dir,output_dir,bruker_name,extension)

    return zarr_job



def call_girder_worker_convert_images_to_nii(input_dir,output_dir,bruker_name,extension):

    nii_job = Job().createLocalJob(
            module='plugin_uct.Tasks',
            function='convert_rec_to_nii',
            title='Convert Rec to Nii',
            type='conversion',
            public=False,
            asynchronous=True
        )
    
    nii_job = task1_convert_rec_to_nii(nii_job,input_dir,output_dir,bruker_name,extension)
   
    return nii_job
