import os
import random
import shutil
import csv

def generate(k):
    root_path = './dataset_aug_ori'

    # new_train_path = './train'
    # new_val_path = './val'

    train_csv_path = f'./train_ori_{k}.csv'
    val_csv_path = f'./val_ori_{k}.csv'

    train_csv = open(train_csv_path, 'w', newline='')
    val_csv = open(val_csv_path, 'w', newline='')

    train_csv_writer = csv.writer(train_csv)
    val_csv_writer = csv.writer(val_csv)

    dirs = os.listdir(root_path)
    for n in range(len(dirs)):
        dir_path = os.path.join(root_path, dirs[n])
        if os.path.isdir(dir_path):
            imgs = os.listdir(dir_path)

            randIdx = []
            for i in range(len(imgs)):
                if i % 5 == k:
                    randIdx.append(0)
                else:
                    randIdx.append(1)

            for i, img in enumerate(imgs):
                img_path = os.path.join(dir_path, img)
                if os.path.isdir(img_path):
                    if randIdx[i]:
                        # new_path = os.path.join(new_train_path, img)
                        train_csv_writer.writerow([img, dirs[n], n])
                    else:
                        # new_path = os.path.join(new_val_path, img)
                        val_csv_writer.writerow([img, dirs[n], n])

                    # shutil.copytree(img_path, new_path)
                        
for i in range(5):
    generate(i)