import os
import boto3

def download_folder_from_s3(bucket_name, prefix, local_dir):

    os.makedirs(local_dir, exist_ok=True)


    s3 = boto3.client('s3')


    objects = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)['Contents']

    for obj in objects:
        # Extract file key and filename
        file_key = obj['Key']
        file_name = os.path.basename(file_key)

        # Create local file path
        local_file_path = os.path.join(local_dir, file_name)

        # Download the file from S3
        s3.download_file(bucket_name, file_key, local_file_path)
        print(f"Downloaded {file_name} to {local_file_path}")

if __name__ == "__main__":
    # Replace these values with your bucket name, prefix, and local directory
    bucket_name = 'cv-train-test-data-dev'
    images_train_prefix = 'dataset-20240407_102817/training_data/images/train/'
    label_train_prefix =  'dataset-20240407_102817/training_data/labels/train/'
    images_val_prefix =  'dataset-20240407_102817/training_data/images/validation/'
    labels_val_prefix =   'dataset-20240407_102817/training_data/labels/validation/'
    local_img_train= 'C:/Users/Basadi Thennakoon/PycharmProjects/4IR/.venv/dataset/images/train'
    local_label_train = 'C:/Users/Basadi Thennakoon/PycharmProjects/4IR/.venv/dataset/labels/train'
    local_img_val = 'C:/Users/Basadi Thennakoon/PycharmProjects/4IR/.venv/dataset/images/validation'
    local_label_val = 'C:/Users/Basadi Thennakoon/PycharmProjects/4IR/.venv/dataset/labels/validation'

    download_folder_from_s3(bucket_name, images_train_prefix, local_img_train)
    download_folder_from_s3(bucket_name, label_train_prefix, local_label_train)
    download_folder_from_s3(bucket_name, images_val_prefix, local_img_val)
    download_folder_from_s3(bucket_name, labels_val_prefix, local_label_val)