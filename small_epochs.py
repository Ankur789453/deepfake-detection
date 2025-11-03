#small epochs test for pretrained model i.e resnet50

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import models, transforms
from PIL import Image
import pandas as pd
import os
from sklearn.model_selection import train_test_split

# =========================
# 1. Dataset Definition
# =========================
class DeepfakeDataset(Dataset):
    def __init__(self, csv_file, transform=None):
        self.data = pd.read_csv(csv_file)
        self.transform = transform

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        row = self.data.iloc[idx]
        img_path = row["frame_path"]
        label = int(row["label"])
        image = Image.open(img_path).convert("RGB")
        if self.transform:
            image = self.transform(image)
        return image, label

# =========================
# 2. Data Transforms
# =========================
transform = transforms.Compose([
    transforms.Resize((224, 224)),   # ResNet50 expects 224x224
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],  # Imagenet normalization
                         std=[0.229, 0.224, 0.225])
])

# =========================
# 3. Load Data from Train/Val Structure
# =========================
# Check if we have the new train/val structure from crop_faces.py
train_real_dir = "data/crops/train/real"
train_fake_dir = "data/crops/train/fake"
val_real_dir = "data/crops/val/real"
val_fake_dir = "data/crops/val/fake"

if os.path.exists(train_real_dir) and os.path.exists(train_fake_dir):
    print("Using train/val split from crop_faces.py")
    
    # Create datasets from directory structure
    train_data = []
    val_data = []
    
    # Load training data
    for img_file in os.listdir(train_real_dir):
        if img_file.endswith('.jpg'):
            train_data.append([os.path.join(train_real_dir, img_file), 0])  # 0 = real
    
    for img_file in os.listdir(train_fake_dir):
        if img_file.endswith('.jpg'):
            train_data.append([os.path.join(train_fake_dir, img_file), 1])  # 1 = fake
    
    # Load validation data
    for img_file in os.listdir(val_real_dir):
        if img_file.endswith('.jpg'):
            val_data.append([os.path.join(val_real_dir, img_file), 0])  # 0 = real
    
    for img_file in os.listdir(val_fake_dir):
        if img_file.endswith('.jpg'):
            val_data.append([os.path.join(val_fake_dir, img_file), 1])  # 1 = fake
    
    # Create DataFrames
    train_df = pd.DataFrame(train_data, columns=['frame_path', 'label'])
    val_df = pd.DataFrame(val_data, columns=['frame_path', 'label'])
    
    print(f"Training samples: {len(train_df)} (Real: {len(train_df[train_df['label']==0])}, Fake: {len(train_df[train_df['label']==1])})")
    print(f"Validation samples: {len(val_df)} (Real: {len(val_df[val_df['label']==0])}, Fake: {len(val_df[val_df['label']==1])})")
    
else:
    # Fallback to CSV method
    csv_file = "data/face_labels.csv"
    if not os.path.exists(csv_file):
        print(f"ERROR: {csv_file} not found and train/val directories don't exist!")
        print("Please run crop_faces.py first to generate the dataset.")
        exit(1)
    
    print("Using CSV file method")
    df = pd.read_csv(csv_file)
    train_df, val_df = train_test_split(df, test_size=0.2, stratify=df["label"], random_state=42)

# Create datasets and data loaders
class DeepfakeDatasetFromDF(Dataset):
    def __init__(self, dataframe, transform=None):
        self.data = dataframe.reset_index(drop=True)
        self.transform = transform

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        row = self.data.iloc[idx]
        img_path = row["frame_path"]
        label = int(row["label"])
        try:
            image = Image.open(img_path).convert("RGB")
            if self.transform:
                image = self.transform(image)
            return image, label
        except Exception as e:
            print(f"Error loading image {img_path}: {e}")
            # Return a black image as fallback
            image = Image.new('RGB', (224, 224), (0, 0, 0))
            if self.transform:
                image = self.transform(image)
            return image, label

train_dataset = DeepfakeDatasetFromDF(train_df, transform=transform)
val_dataset = DeepfakeDatasetFromDF(val_df, transform=transform)

train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True, num_workers=0)
val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False, num_workers=0)

# =========================
# 4. Load Pretrained ResNet50
# =========================
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Using device:", device)

model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)

# Freeze all layers except the last fully connected
for param in model.parameters():
    param.requires_grad = False

# Replace final FC layer for 2 classes (real/fake)
num_ftrs = model.fc.in_features
model.fc = nn.Linear(num_ftrs, 2)

model = model.to(device)

# =========================
# 5. Loss & Optimizer
# =========================
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.fc.parameters(), lr=0.001)

# =========================
# 6. Training Loop with Validation
# =========================
epochs = 5
best_val_acc = 0.0

for epoch in range(epochs):
    # Training phase
    model.train()
    running_loss, correct, total = 0.0, 0, 0

    for images, labels in train_loader:
        images, labels = images.to(device), labels.to(device)

        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item()
        _, predicted = torch.max(outputs, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()

    train_acc = 100 * correct / total
    avg_train_loss = running_loss / len(train_loader)
    
    # Validation phase
    model.eval()
    val_loss, val_correct, val_total = 0.0, 0, 0
    
    with torch.no_grad():
        for images, labels in val_loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            loss = criterion(outputs, labels)
            
            val_loss += loss.item()
            _, predicted = torch.max(outputs, 1)
            val_total += labels.size(0)
            val_correct += (predicted == labels).sum().item()
    
    val_acc = 100 * val_correct / val_total
    avg_val_loss = val_loss / len(val_loader)
    
    print(f"Epoch [{epoch+1}/{epochs}]")
    print(f"  Train - Loss: {avg_train_loss:.4f}, Acc: {train_acc:.2f}%")
    print(f"  Val   - Loss: {avg_val_loss:.4f}, Acc: {val_acc:.2f}%")
    
    # Save best model
    if val_acc > best_val_acc:
        best_val_acc = val_acc
        torch.save({
            'epoch': epoch + 1,
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'val_acc': val_acc,
            'train_acc': train_acc
        }, 'best_deepfake_model.pth')
        print(f"  ✓ New best model saved! Val Acc: {val_acc:.2f}%")
    print()

# =========================
# 7. Final Results
# =========================
print(f"\n=== Training Complete ===")
print(f"Best Validation Accuracy: {best_val_acc:.2f}%")
print(f"Model saved as: best_deepfake_model.pth")
print(f"\n✅ Training completed successfully!")

# Load best model for final evaluation
print("\nLoading best model for final validation...")
checkpoint = torch.load('best_deepfake_model.pth')
model.load_state_dict(checkpoint['model_state_dict'])

model.eval()
final_correct, final_total = 0, 0
with torch.no_grad():
    for images, labels in val_loader:
        images, labels = images.to(device), labels.to(device)
        outputs = model(images)
        _, predicted = torch.max(outputs, 1)
        final_total += labels.size(0)
        final_correct += (predicted == labels).sum().item()

final_acc = 100 * final_correct / final_total
print(f"Final Validation Accuracy: {final_acc:.2f}%")
