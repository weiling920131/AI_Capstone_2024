import os
import cv2
import vidaug.augmentors as va
import shutil

dataset_dir = './dataset_ori'
output_dir = './dataset_aug_ori'
shutil.copytree(dataset_dir, output_dir)
sometimes = lambda aug: va.Sometimes(0.5, aug) # Used to apply augmentor with 50% probability

for category in os.listdir(output_dir):
    category_path = os.path.join(output_dir, category)
    done = False
    while not done:
        for video in os.listdir(category_path):
            video_path = os.path.join(category_path, video)
            if not os.path.isdir(video_path):
                continue
            
            folder_i = len([file for file in os.listdir(category_path) if os.path.isdir(os.path.join(category_path, file))]) + 1
            if folder_i > 200:
                done = True
                print(category)
                break
            
            folder_name = f"{category}_{str(folder_i).zfill(4)}"
            os.makedirs(os.path.join(category_path, folder_name), exist_ok=True)
            frames = [] 
            for frame in os.listdir(video_path):
                frame_path = os.path.join(video_path, frame)
                img = cv2.imread(frame_path, cv2.IMREAD_COLOR)
                frames.append(img)

            seq = va.Sequential([sometimes(va.HorizontalFlip()),
                            sometimes(va.RandomShear(-0.1, 0.1)),
                            sometimes(va.RandomTranslate(5, 5))])
            #augment the frames
            img_aug = seq(frames)
            for frame in img_aug:
                # output the video
                frame_i = len([file for file in os.listdir(os.path.join(category_path, folder_name))]) + 1
                cv2.imwrite(os.path.join(os.path.join(category_path, folder_name), f"frame_{str(frame_i).zfill(3)}.jpg"), frame)



    