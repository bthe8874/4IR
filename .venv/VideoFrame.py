import os
import boto3
import  cv2
import subprocess

s3=boto3.client('s3')
bucket = 'cv-footage'
footage_key = '013 CTX Dock/Export 12-5-2023 Dry Dock/013 WH Dry Dock 17-22 (192)/12_3_2023 5_59_59 PM (UTC-06_00).mkv'

frame_output_directory = 'Frames'
os.makedirs(frame_output_directory,exist_ok=True)

videoframe_output_directory = "VideoFrames"
os.makedirs(videoframe_output_directory,exist_ok = True)


def read_footage_from_s3(bucket_name , footage_name):
    video_uri = s3.generate_presigned_url( ClientMethod='get_object', Params={ 'Bucket': bucket_name, 'Key': footage_name} )
    video_capture = cv2.VideoCapture(video_uri)

    if not video_capture.isOpened():
        print("Error loading the video")
        exit()

    return video_capture


def frame_the_footage(frame_counter , target_frame_count , video_captured , output_directory , frame_extracrion_interval):

    while True:

        video_captured.set(cv2.CAP_PROP_POS_FRAMES, frame_counter * frame_extraction_interval)

        video_returned , frame = video_captured.read()
        if not video_returned:
            print("error")
            exit()
        cv2.imwrite(os.path.join(output_directory,f'frame_{frame_counter}.jpg'),frame)

        frame_counter += 1
        print("frame_counter",frame_counter)
        if frame_counter >= target_frame_count:
            print("exceeded")
            break

    return frame_counter

def extract_video_clips(frame_counter , target_clip_count , video_captured , output_directory , clip_duration_seconds , fps ,  frame_extraction_interval):

    clip_counter = 0
    print("clip count", clip_counter)
    while clip_counter < target_clip_count:
        start_frame = frame_counter
        end_frame = start_frame + int(clip_duration_seconds * fps)
        video_captured.set(cv2.CAP_PROP_POS_FRAMES , start_frame*frame_extraction_interval)
        frames = []
        while frame_counter < end_frame:
            ret , cap = video_captured.read()
            if not ret :
                break
            frames.append(cap)
            frame_counter+=1
        if frames:
            clip_path = os.path.join(output_directory , f'clip_{clip_counter}.mp4')
            print("clip path", clip_path)
            out_video = cv2.VideoWriter(
                clip_path ,
                cv2.VideoWriter_fourcc(*'mp4v'),
                fps ,
                (frames[0].shape[1],frames[0].shape[0]))
            for frame in frames:
                out_video.write(frame)
            out_video.release()
            clip_counter+=1
            print("clip counter",clip_counter)
    return frame_counter

def split_video(input_file, output_pattern, segment_duration, output_dir):
    # Ensure the output directory exists, create it if it doesn't
    os.makedirs(output_dir, exist_ok=True)

    # Construct the output file path using the output directory and pattern
    output_file = os.path.join(output_dir, output_pattern)

    # Construct the FFmpeg command
    ffmpeg_command = [
        'ffmpeg', '-i', input_file,
        '-c', 'copy', '-map', '0', '-segment_time', str(segment_duration),
        '-f', 'segment', output_file
    ]

    # Run FFmpeg command
    subprocess.run(ffmpeg_command)


output_pattern = 'output_%03d.mp4'  # Output file naming pattern
segment_duration = 7200  # Segment duration in seconds (2 hours)
output_directory = 'output_videos'
input_video = 'C:/Users/Basadi Thennakoon/Downloads/12_3_2023 5_59_59 PM (UTC-06_00) (1).mkv'


frame_counter = 0
target_frame_count = 1000
target_clip_count = 10
clip_duration_seconds = 4
video_capture = read_footage_from_s3(bucket,footage_key)

total_frames = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
fps = video_capture.get(cv2.CAP_PROP_FPS)
frame_extraction_interval = total_frames // target_frame_count

print("total frames",total_frames)

frames_per_hour = total_frames // 12
frames_per_min = frames_per_hour // 60
frames_per_second = frames_per_min // 60

print("fps",fps)

split_video(input_video, output_pattern, segment_duration, output_directory)
#frame_counter=frame_the_footage(0,1000,video_capture,frame_output_directory , frame_extraction_interval)
#frame_counter = extract_video_clips(0,target_clip_count , video_capture , videoframe_output_directory ,clip_duration_seconds ,fps , frame_extraction_interval)
video_capture.release()
print("frame",frame_counter)


