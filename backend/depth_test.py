import torch
import cv2
import numpy as np
from PIL import Image
import pillow_heif
import matplotlib.pyplot as plt


# Using MiDaS for faster and simple depth estimation
model_type = "DPT_Large"
midas = torch.hub.load("intel-isl/MiDaS", model_type, trust_repo = True)
midas.eval()

transform = torch.hub.load("intel-isl/MiDaS", "transforms").dpt_transform

# load a test image
pillow_heif.register_heif_opener()

img = Image.open("/Users/prajjwal/Downloads/IMG_5680.HEIC")
img = np.array(img)
print(img.shape)

input_batch = transform(img)
print(input_batch.shape)

with torch.no_grad():
    prediction = midas(input_batch)
    prediction = torch.nn.functional.interpolate(
        prediction.unsqueeze(1),
        size = img.shape[: 2],
        mode = "bicubic",
        align_corners = False,
    ).squeeze()

depth = prediction.cpu().numpy()

# Normalize
depth_norm = (depth - depth.min()) / (depth.max() - depth.min())

# save depth image
plt.imshow(depth_norm, cmap = "inferno")
plt.axis("off")
plt.savefig("depth.png")

print("Depth map saved at depth.png")

# resize depth to 20x20 grid
grid_size = 20
depth_small = cv2.resize(depth_norm, (grid_size, grid_size))

# smooth noise
depth_small = cv2.GaussianBlur(depth_small, (3,3), 0)

# safe normalization
min_val = depth_small.min()
max_val = depth_small.max()

if max_val - min_val > 1e-6:
    depth_small = (depth_small - min_val) / (max_val - min_val)
else:
    depth_small = np.zeros_like(depth_small)

# improve contrast
depth_uint8 = (depth_small * 255).astype(np.uint8)
depth_eq = cv2.equalizeHist(depth_uint8)
depth_small = depth_eq / 255.0

# multi-thresholding
grid = np.zeros_like(depth_small)

# close objects
grid[depth_small > 0.6] = 1

# mid-range objects
grid[(depth_small > 0.4) & (depth_small <= 0.6)] = 1

# dilation (makes obstacles usable in game)
kernel = np.ones((2,2), np.uint8)
grid = cv2.dilate(grid.astype(np.uint8), kernel, iterations=1)

print("Grid:")
print(grid)

plt.imshow(grid, cmap="gray")
plt.title("Occupancy Grid")
plt.show()

spawn_points = []

for i in range(grid_size):
    # top edge
    if grid[0][i] == 0:
        spawn_points.append([0, i])
    # bottom edge
    if grid[grid_size-1][i] == 0:
        spawn_points.append([grid_size-1, i])
    # left edge
    if grid[i][0] == 0:
        spawn_points.append([i, 0])
    # right edge
    if grid[i][grid_size-1] == 0:
        spawn_points.append([i, grid_size-1])

# limit to 3
spawn_points = spawn_points[:3]

print("Spawns:", spawn_points)

import json

output = {
    "grid": grid.tolist(),
    "spawns": spawn_points
}

with open("output.json", "w") as f:
    json.dump(output, f)

print("Saved output.json")