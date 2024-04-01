import numpy as np
import cv2
import os

def extract_frames(video_path, output_dir):

    video = cv2.VideoCapture(video_path)
    os.makedirs(output_dir, exist_ok=True)
    
    cnt = 1
    frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT) / 30)
    if frame_count == 0:
        frame_count = 1

    success, frame = video.read()
    if success: frame = cv2.resize(frame, (160, 90))
    
    last_frame = frame
    while success:
        if cnt > 30:
            break
        output_path = os.path.join(output_dir, f"frame_{str(cnt).zfill(3)}.jpg")
        cv2.imwrite(output_path, frame)
        cnt += 1
        
        for _ in range(frame_count):
            success, frame = video.read()
            if not success:
                break
            frame = cv2.resize(frame, (160, 90))
            last_frame = frame

    if cnt <= 30:
        for i in range(cnt, 31):
            output_path = os.path.join(output_dir, f"frame_{str(i).zfill(3)}.jpg")
            cv2.imwrite(output_path, last_frame)


if __name__ == "__main__":
    dataset_dir = "./dataset"
    for catagory in os.listdir(dataset_dir):
        cnt = 1
        catagory_path = os.path.join(dataset_dir, catagory)
        for video in os.listdir(catagory_path):
            video_path = os.path.join(catagory_path, video)
            if os.path.isdir(video_path):
                continue
            extract_frames(video_path, os.path.join(catagory_path, f"{catagory}_{str(cnt).zfill(4)}"))
            print("done")
            cnt += 1

