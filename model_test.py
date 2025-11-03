
import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
import sys

# -------------------
# CONFIG
# -------------------
MODEL_PATH = "best_deepfake_model.pth"   # your trained model
CLASS_NAMES = ["real", "fake"]           # update if your labels are different
IMAGE_SIZE = 128                         # same as you trained

# -------------------
# Load Model
# -------------------
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load ResNet50
model = models.resnet50(weights=None)  # no pretrained, since you trained already
num_features = model.fc.in_features
model.fc = nn.Linear(num_features, len(CLASS_NAMES))  # output layer = 2 classes

# Load checkpoint
checkpoint = torch.load(MODEL_PATH, map_location=device)
model.load_state_dict(checkpoint["model_state_dict"])   # ✅ only weights
model.to(device)
model.eval()

print("✅ Model loaded successfully!")

# -------------------
# Image Preprocessing
# -------------------
transform = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225]),
])

def predict(image_path):
    image = Image.open(image_path).convert("RGB")
    img_tensor = transform(image).unsqueeze(0).to(device)

    with torch.no_grad():
        outputs = model(img_tensor)
        _, preds = torch.max(outputs, 1)
        prob = torch.softmax(outputs, dim=1)[0][preds].item()

    label = CLASS_NAMES[preds.item()]
    return label, prob

# -------------------
# Run Prediction
# -------------------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python model_test.py <image_path>")
        sys.exit(1)

    image_path = sys.argv[1]
    label, prob = predict(image_path)
    print(f"🖼️ Image: {image_path}")
    print(f"🔮 Prediction: {label} ({prob*100:.2f}%)")
