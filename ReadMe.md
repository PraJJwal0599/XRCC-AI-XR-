# 🏠 Room Defense AI

Turn your real-world room into a playable game using AI.

## 🚀 Idea

Upload a photo of your room → AI converts it into a grid map → a browser-based game simulates enemies navigating your space.

---

## 🧠 How it Works

1. **Image Input**
   - User uploads a room image (JPG, PNG, HEIC supported)

2. **AI Processing (Python)**
   - Monocular depth estimation using MiDaS
   - Depth map → occupancy grid (20x20)
   - Detect walkable areas and obstacles
   - Generate spawn points

3. **Game Engine (Browser)**
   - Grid rendered using Phaser.js
   - Enemies spawn and use A* pathfinding
   - Player placed in safe location
   - Simulation runs in real-time

---

## 🧱 Tech Stack

### Backend (AI + API)
- Python
- FastAPI
- PyTorch (MiDaS)
- OpenCV
- NumPy
- Pillow + pillow-heif (for HEIC support)

### Frontend (Game)
- Phaser.js
- EasyStar.js (A* pathfinding)
- Vanilla HTML/JS

---

## 🎮 Features

- 📸 Real-world room → playable map
- 🧠 AI-based depth understanding
- 🗺️ Automatic grid generation
- 🤖 Intelligent enemy navigation
- 🌐 Runs entirely in browser (no install)

---

## ⚙️ Setup Instructions

### 1. Clone the repo

### bash
git clone <repo-url>
cd ROOMDEFENCE_AI+XR

### Backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
run requirements file

uvicorn main:app --reload (run backend)

### Frontend
python -m http.server 8080
