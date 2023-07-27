import os
import glob
import random
import itertools
import cv2

def resize_image(image, target_size):
    return cv2.resize(image, target_size, interpolation=cv2.INTER_AREA)

# 指定目标尺寸
target_size = (100, 100)

# 获取所有图片文件的路径
folder_path = 'D:/RobotCar/myCode/alphabet/Number/'
base_folders = ['base1', 'base2', 'base3', 'base4']
digits = range(10)

image_paths = {}
for base_folder in base_folders:
    for digit in digits:
        digit_paths = glob.glob(os.path.join(folder_path, base_folder, f"{digit}.jpg"))
        image_paths[f"{base_folder}_{digit}"] = digit_paths[0]

# 生成所有可能的组合（不重复）
combinations = list(itertools.combinations(digits, 2))
random.shuffle(combinations)
combinations = combinations[:10]

# 为每个组合创建一个组合图像
for comb in combinations:
    images = []
    for digit in comb:
        base_folder = random.choice(base_folders)
        img_path = image_paths[f"{base_folder}_{digit}"]
        img = cv2.imread(img_path)
        img_resized = resize_image(img, target_size)
        images.append(img_resized)

    combined_image = cv2.hconcat(images)

    # 保存组合后的图像
    image_name = ''.join(map(str, comb)) + '.jpg'
    output_path = os.path.join(folder_path, 'output', image_name)
    cv2.imwrite(output_path, combined_image)
