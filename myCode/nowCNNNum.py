from PIL import Image
import torch
import torchvision.transforms as transforms
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from torch import nn

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
    nn.Linear(64*7*7, 64),
    nn.ReLU(),
    nn.Linear(64, 10)
)
model.load_state_dict(torch.load('my_model.pth'))
model.eval()  # 设置为评估模式

# 加载图像
img = Image.open('D:/RobotCar/result1/alphabet/Number/templete/train/4/16.jpg')

# 转换图像到灰度
img = img.convert('L')
img = img.resize((28,28))
# 转换图像并添加维度
transform = transforms.Compose([transforms.ToTensor()])
img = transform(img)
img.unsqueeze_(0)

# 通过模型进行预测
with torch.no_grad():
    output = model(img)

# 获取预测结果
_, predicted = torch.max(output, 1)
# 假设我们有一个从类别索引到标签的列表
class_to_label = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

# 我们可以使用预测的类别索引来获取标签
predicted_label = class_to_label[predicted.item()]

print(predicted_label)
# 创建图像
# 去掉批量维度
img = img.squeeze(0)

fig, ax = plt.subplots(1)

# 转换通道维度
img = img.permute(1, 2, 0)

# 显示图像
ax.imshow(img, cmap='gray')

# 显示图像
ax.imshow(img.permute(1, 2, 0).squeeze(), cmap='gray')

# 创建一个矩形框并添加到图像上
rect = patches.Rectangle((50, 50), 40, 30, linewidth=1, edgecolor='r', facecolor='none')
ax.add_patch(rect)

# 在图像上显示预测结果
plt.text(50, 50, str(predicted.item()), color='red')

plt.show()
