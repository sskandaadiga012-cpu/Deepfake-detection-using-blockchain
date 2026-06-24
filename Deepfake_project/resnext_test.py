import torch
import torchvision.models as models

# Step 1: Load official pretrained ResNeXt model
model = models.resnext50_32x4d(weights="IMAGENET1K_V1")

# Step 2: Print model structure (optional)
print(model)

# Step 3: Test with dummy input (VERY IMPORTANT)
dummy_input = torch.randn(1, 3, 224, 224)

# Step 4: Forward pass
output = model(dummy_input)

# Step 5: Print output shape
print("Output shape:", output.shape)

print("✅ ResNeXt model loaded and working successfully!")
