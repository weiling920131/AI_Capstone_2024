import os

dataset_path = './dataset'

for category in os.listdir(dataset_path):
    category_path = os.path.join(dataset_path, category)
    for vid in os.listdir(category_path):
        prev_path = os.path.join(category_path, vid)
        new_path = prev_path[:-3] + '0' + prev_path[-3:]
        print(new_path)
        os.rename(prev_path, new_path)