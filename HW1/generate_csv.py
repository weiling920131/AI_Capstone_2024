import os
import csv

root_path = './dataset_aug'

csv_path = './dataset_aug.csv'
csv_writer = csv.writer(open(csv_path, 'w', newline=''))

dirs = os.listdir(root_path)
for n in range(len(dirs)):
    dir_path = os.path.join(root_path, dirs[n])
    if os.path.isdir(dir_path):
        imgs = os.listdir(dir_path)
        for img in imgs:
            img_path = os.path.join(dir_path, img)
            if os.path.isdir(img_path):
                csv_writer.writerow([img, dirs[n], n])