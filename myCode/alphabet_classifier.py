from PIL import Image
import torch
import torchvision.transforms as transforms
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from torch import nn
import cv2
import numpy as np

# 加载模型
# 初始化模型
model = nn.Sequential(
    nn.Conv2d(1, 32, kernel_size=3, stride=1, padding=1),
    nn.ReLU(),
    nn.MaxPool2d(kernel_size=2, stride=2),
    nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1),
    nn.ReLU(),
    nn.MaxPool2d(kernel_size=2, stride=2),
    nn.Flatten(),
    nn.Linear(64 * 7 * 7, 64),
    nn.ReLU(),
    nn.Linear(64, 10)
)
model.load_state_dict(torch.load('my_model.pth'))
model.eval()  # 设置为评估模式

# 加载图像
img = Image.open('D:/RobotCar/result1/alphabet/Number/output/124.jpg')

# 转换图像到灰度
img = img.convert('L')

# 转换图像并添加维度
transform = transforms.Compose([transforms.ToTensor()])

window_size = 95
step_size = 95

# 假设我们有一个从类别索引到标签的列表
class_to_label = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

# 创建图像
fig, ax = plt.subplots(1)

# 显示图像
ax.imshow(img, cmap='gray')

count=0
for i in range(0, img.width - window_size, step_size):
    count+=1
    # 提取窗口
    window = img.crop((i, 1, i + window_size, window_size))

    window=window.resize((28 , 28))
    if (count == 3):
        aera1_crop = np.array(window)
        cv2.imwrite("D:/RobotCar/result1/alphabet/Number/templete/train/4/16.jpg", aera1_crop)

    # 转换窗口并添加维度

    window_tensor = transform(window)
    window_tensor.unsqueeze_(0)


    # 通过模型进行预测
    with torch.no_grad():
        output = model(window_tensor)

    # 获取预测结果
    _, predicted = torch.max(output, 1)

    # 我们可以使用预测的类别索引来获取标签
    predicted_label = class_to_label[predicted.item()]

    print(f'Position: {i}, Predicted label: {predicted_label}')

    # 创建一个矩形框并添加到图像上
    rect = patches.Rectangle((i, 0), window_size, window_size, linewidth=1, edgecolor='r', facecolor='none')
    ax.add_patch(rect)

    # 在图像上显示预测结果
    plt.text(i, window_size / 2, str(predicted.item()), color='red')

plt.show()
