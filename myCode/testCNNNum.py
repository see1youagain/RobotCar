import torch
import torchvision
from torchvision import transforms
from torch.utils.data import DataLoader
from torch import nn
import os

def main():
    # 数据增强和加载
    data_transforms = {
        'train': transforms.Compose([
            transforms.Grayscale(),
            transforms.Resize((28,28)),
            transforms.RandomRotation(20),
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
        ]),
        'val': transforms.Compose([
            transforms.Grayscale(),
            transforms.Resize((28,28)),
            transforms.ToTensor(),
        ]),
    }

    data_dir = 'D:/RobotCar/result1/alphabet/Number/templete'
    image_datasets = {x: torchvision.datasets.ImageFolder(os.path.join(data_dir, x),
                                                          data_transforms[x])
                      for x in ['train', 'val']}

    dataloaders = {x: DataLoader(image_datasets[x], batch_size=4,
                                 shuffle=True, num_workers=0) # 在Windows环境下设置 num_workers=0
                  for x in ['train', 'val']}

    # 定义模型
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

    # 定义损失函数和优化器
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    # 训练模型
    for epoch in range(70):
        for phase in ['train', 'val']:
            if phase == 'train':
                model.train()
            else:
                model.eval()

            running_loss = 0.0
            running_corrects = 0

            for inputs, labels in dataloaders[phase]:
                optimizer.zero_grad()

                with torch.set_grad_enabled(phase == 'train'):
                    outputs = model(inputs)
                    _, preds = torch.max(outputs, 1)
                    loss = criterion(outputs, labels)

                    if phase == 'train':
                        loss.backward()
                        optimizer.step()

                running_loss += loss.item() * inputs.size(0)
                running_corrects += torch.sum(preds == labels.data)

            epoch_loss = running_loss / len(dataloaders[phase].dataset)
            epoch_acc = running_corrects.double() / len(dataloaders[phase].dataset)

            print('{} Loss: {:.4f} Acc: {:.4f}'.format(phase, epoch_loss, epoch_acc))
    torch.save(model.state_dict(), 'my_model.pth')


if __name__ == '__main__':
    main()
