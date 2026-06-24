import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
import os

print("Loading ResNeXt model...")

# 1️⃣ Load pretrained ResNeXt
model = models.resnext50_32x4d(weights="IMAGENET1K_V1")

# 2️⃣ Remove classification layer (VERY IMPORTANT)
model = torch.nn.Sequential(*list(model.children())[:-1])
model.eval()

print("Model ready!")

# 3️⃣ Image preprocessing
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

# 4️⃣ Dataset path
data_path = "faces/train"
classes = ["real", "fake"]

features = []
labels = []

# 5️⃣ Loop through images
for label, c in enumerate(classes):
    folder = os.path.join(data_path, c)

    for img_name in os.listdir(folder):

        img_path = os.path.join(folder, img_name)

        try:
            img = Image.open(img_path).convert("RGB")
        except:
            continue

        img = transform(img)
        img = img.unsqueeze(0)

        with torch.no_grad():
            feature = model(img)

        feature = feature.view(-1)  # convert to 2048 vector

        features.append(feature)
        labels.append(label)

    print(f"Done: {c}")

# 6️⃣ Convert to tensors
features = torch.stack(features)
labels = torch.tensor(labels)

# 7️⃣ Save features
torch.save(features, "features.pt")
torch.save(labels, "labels.pt")

print("✅ Feature extraction completed!")
print("Feature shape:", features.shape)