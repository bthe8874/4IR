from ultralytics import YOLO
import os
import json
import boto3

s3_client = boto3.client('s3')

# Function to list all objects in a given S3 folder
def list_objects_in_folder(bucket, s3_folder):
    response = s3_client.list_objects_v2(Bucket=bucket, Prefix=s3_folder)
    for obj in response.get('Contents', []):
        yield obj['Key']

def download_json_files(s3_bucket , s3_folder , local_dir):
    os.makedirs(local_dir , exist_ok=True)

    for file_key in list_objects_in_folder(s3_bucket , s3_folder):
        if file_key.endswith('/') or not file_key.endswith('.json'):
            continue
        local_file_path = os.path.join(local_dir, file_key.split('/')[-1])
        s3_client.download_file(s3_bucket, file_key, local_file_path)
        print(f"Downloaded JSON file: {local_file_path}")



# Function to convert JSON labels to YOLO format
def convert_labels_to_yolo(json_folder, yolo_folder):
    for json_file in os.listdir(json_folder):
        if json_file.endswith('.json'):
            with open(os.path.join(json_folder, json_file), 'r') as f:
                data = json.load(f)
                yolo_labels = []
                for annotation in data['answers']:
                    for bounding_box in annotation['answerContent']['boundingBox']['boundingBoxes']:
                        class_id = get_class_id(bounding_box['label'])
                        image_width = data['answers'][0]['answerContent']['inputImageProperties']['width']
                        image_height = data['answers'][0]['answerContent']['inputImageProperties']['height']
                        center_x, center_y, width, height = get_yolo_coordinates(bounding_box , image_width , image_height)
                        yolo_labels.append(f"{class_id} {center_x} {center_y} {width} {height}")

                yolo_filename = os.path.splitext(json_file)[0] + '.txt'
                with open(os.path.join(yolo_folder, yolo_filename), 'w') as yolo_file:
                    yolo_file.write('\n'.join(yolo_labels))


# Function to map object labels to YOLO class IDs
def get_class_id(label):
    if label == 'Vehicles':
        return 0
    elif label == 'Goods':
        return 1
    elif label == 'People':
        return 2
    elif label == 'Pallets':
        return 3
    else:
        return -1

# Function to calculate YOLO coordinates from bounding box data
def get_yolo_coordinates(bounding_box , image_width , image_height):
    center_x = (bounding_box['left'] + bounding_box['width'] / 2) / image_width
    center_y = (bounding_box['top'] + bounding_box['height'] / 2) / image_height
    width = bounding_box['width'] / image_width
    height = bounding_box['height'] / image_height
    return center_x, center_y, width, height



s3_bucket = 'cv-groundtruth-test'
s3_folder = 'generated_frames/dataset-20240405_041127/image_labels/EAGLJ-20240414152450-basadee/annotations/worker-response/iteration-1'
json_directory = 'local_json_dir'

# for folder_key in list_objects_in_folder(s3_bucket, s3_folder):
#     print(folder_key)
#     if not folder_key.endswith('/'):
#         continue
#
#     folder_objects = list_objects_in_folder(s3_bucket, folder_key)
#     # print(folder_objects)
#     for json_file_key in folder_objects:
#         if json_file_key.endswith('/') or not json_file_key.endswith('.json'):
#             continue
#         s3_client.download_file(s3_bucket, json_file_key,
#                                 json_file_key.split('/')[-1])
#         print(f"Processed JSON file: {json_file_key.split('/')[-1]}")



download_json_files(s3_bucket, s3_folder, json_directory)

    # Convert JSON labels to YOLO format
    #convert_labels_to_yolo(local_folder, yolo_folder)



