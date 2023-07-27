
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
import numpy as np
from custom_dataset import CustomDataset,DigitRecognizer
import cv2

# Load data and labels
train_data = np.load('train_data.npy')
train_labels = np.load('train_labels.npy')
val_data = np.load('val_data.npy')
val_labels = np.load('val_labels.npy')

# Set up transformations
transform = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize((100, 100)),
    transforms.ToTensor()
])

# Create the datasets and dataloaders
batch_size = 32
train_dataset = CustomDataset(train_data, train_labels, transform)
val_dataset = CustomDataset(val_data, val_labels, transform)
train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

# Instantiate the model, loss, and optimizer
model = DigitRecognizer()
criterion = nn.CrossEntropyLoss()
optimizer = optim.SGD(model.parameters(), lr=0.009, momentum=0.9)

# Train the model
num_epochs = 100
for epoch in range(num_epochs):
    running_loss = 0.0
    for i, (inputs, labels) in enumerate(train_loader):
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        running_loss += loss.item()

    print(f'Epoch {epoch + 1}, Loss: {running_loss / (i + 1)}')

    # Validate the model
    with torch.no_grad():
        correct = 0
        total = 0
        for images, labels in val_loader:
            outputs = model(images)
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
        print(f'Validation Accuracy: {(100 * correct / total):.2f}%')

# Save the trained model
torch.save(model.state_dict(), 'digit_recognizer.pth')
