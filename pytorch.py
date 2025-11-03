import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image
import pandas as pd

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

transform = transforms.Compose([
    transforms.Resize((128, 128)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
])

def main():
    csv_file = "data/face_labels.csv"
    dataset = DeepfakeDataset(csv_file, transform=transform)

    dataloader = DataLoader(dataset, batch_size=32, shuffle=True, num_workers=0)  # 👈 use 0 on Windows

    batch = next(iter(dataloader))
    images, labels = batch
    print("✅ Batch loaded successfully!")
    print("Images shape:", images.shape)
    print("Labels shape:", labels.shape)

if __name__ == "__main__":
    main()
