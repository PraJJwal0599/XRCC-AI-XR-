import torch
import cv2
import numpy as np

# ==============================
# LOAD MODEL ONCE (IMPORTANT)
# ==============================
model_type = "DPT_Large"
midas = torch.hub.load("intel-isl/MiDaS", model_type)
midas.eval()

transform = torch.hub.load("intel-isl/MiDaS", "transforms").dpt_transform


# ==============================
# MAIN FUNCTION
# ==============================
def process_image(image):
    """
    Input: OpenCV image (BGR)
    Output: grid (list), spawn points (list)
    """

    # Convert to RGB for model
    img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Transform for model
    input_batch = transform(img)

    if input_batch.dim() == 3:
        input_batch = input_batch.unsqueeze(0)

    # ==============================
    # DEPTH PREDICTION
    # ==============================
    with torch.no_grad():
        prediction = midas(input_batch)
        prediction = torch.nn.functional.interpolate(
            prediction.unsqueeze(1),
            size=img.shape[:2],
            mode="bicubic",
            align_corners=False,
        ).squeeze()

    depth = prediction.cpu().numpy()

    # ==============================
    # NORMALIZE DEPTH
    # ==============================
    min_val = depth.min()
    max_val = depth.max()

    if max_val - min_val > 1e-6:
        depth_norm = (depth - min_val) / (max_val - min_val)
    else:
        depth_norm = np.zeros_like(depth)

    # ==============================
    # GRID GENERATION
    # ==============================
    grid_size = 20

    # Resize to grid
    depth_small = cv2.resize(depth_norm, (grid_size, grid_size))

    # Smooth noise
    depth_small = cv2.GaussianBlur(depth_small, (3, 3), 0)

    # Re-normalize after blur
    min_val = depth_small.min()
    max_val = depth_small.max()

    if max_val - min_val > 1e-6:
        depth_small = (depth_small - min_val) / (max_val - min_val)
    else:
        depth_small = np.zeros_like(depth_small)

    # Improve contrast
    depth_uint8 = (depth_small * 255).astype(np.uint8)
    depth_eq = cv2.equalizeHist(depth_uint8)
    depth_small = depth_eq / 255.0

    # ==============================
    # THRESHOLDING (MULTI-LEVEL)
    # ==============================
    grid = np.zeros_like(depth_small)

    # Close objects
    grid[depth_small > 0.6] = 1

    # Mid-range objects
    grid[(depth_small > 0.4) & (depth_small <= 0.6)] = 1

    # ==============================
    # MORPHOLOGICAL CLEANUP
    # ==============================
    kernel = np.ones((2, 2), np.uint8)
    grid = cv2.dilate(grid.astype(np.uint8), kernel, iterations=1)

    # ==============================
    # SPAWN POINT DETECTION
    # ==============================
    spawns = []

    for i in range(grid_size):
        # top
        if grid[0][i] == 0:
            spawns.append([0, i])

        # bottom
        if grid[grid_size - 1][i] == 0:
            spawns.append([grid_size - 1, i])

        # left
        if grid[i][0] == 0:
            spawns.append([i, 0])

        # right
        if grid[i][grid_size - 1] == 0:
            spawns.append([i, grid_size - 1])

    # Limit spawns
    spawns = spawns[:3]

    # ==============================
    # RETURN JSON-READY DATA
    # ==============================
    return grid.tolist(), spawns