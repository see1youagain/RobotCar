import numpy as np
import torch.nn.functional as F
from torch import nn
import torch
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import torchvision.transforms as transforms

# 修改原始模型，使其可以处理多个数字
class MultiDigitModel(nn.Module):
    def __init__(self):
        super(MultiDigitModel, self).__init__()
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, stride=1, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1)
        self.fc1 = nn.Linear(64 * 7 * 7, 64)
        self.fc2 = nn.Linear(64, 10)
        self.fc3 = nn.Linear(64, 1)  # 额外的输出层，用于预测是否存在数字

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.max_pool2d(x, kernel_size=2, stride=2)
        x = F.relu(self.conv2(x))
        x = F.max_pool2d(x, kernel_size=2, stride=2)
        x = x.view(x.size(0), -1)
        x = F.relu(self.fc1(x))
        digit = self.fc2(x)
        exist = torch.sigmoid(self.fc3(x))  # 使用sigmoid激活函数，因为这是一个二分类问题
        return digit, exist


model = MultiDigitModel()
model.load_state_dict(torch.load('my_model.pth'))
model.eval()  # 设置为评估模式

# 加载图像
img = Image.open('D:/RobotCar/result1/alphabet/Number/output/012.jpg')

# 转换图像到灰度
img = img.convert('L')

# 假设我们有一个从类别索引到标签的列表
class_to_label = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

# 创建图像
fig, ax = plt.subplots(1)

# 显示图像
ax.imshow(img, cmap='gray')

# 滑动窗口的大小
window_size = 28
# 滑动窗口的步长
step_size = 14

# 转换图像并添加维度
transform = transforms.Compose([transforms.ToTensor()])

for i in range(0, img.width - window_size, step_size):
    # 提取窗口
    window = img.crop((i, 0, i + window_size, window_size))

    # 转换窗口并添加维度
    window_tensor = transform(window)
    window_tensor.unsqueeze_(0)

    # 通过模型进行预测
    with torch.no_grad():
        digit, exist = model(window_tensor)

    # 获取预测结果
    _, predicted = torch.max(digit, 1)
    exist = (exist > 0.5).item()  # 根据是否存在数字的预测结果，确定是否存在数字

    if exist:
        # 我们可以使用预测的类别索引来获取标签
        predicted_label = class_to_label[predicted.item()]

        print(f'Position: {i}, Predicted label: {predicted_label}')

        # 创建一个矩形框并添加到图像上
        rect = patches.Rectangle((i, 0), window_size, window_size, linewidth=1, edgecolor='r', facecolor='none')
        ax.add_patch(rect)

        # 在图像上显示预测结果
        plt.text(i, window_size, str(predicted.item()), color='red')

        plt.show()

