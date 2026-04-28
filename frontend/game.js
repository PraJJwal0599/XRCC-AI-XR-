const gridSize = 20;
const tileSize = 30;

let currentScene;
let grid = [];
let enemies = [];
let player;

const config = {
    type: Phaser.AUTO,
    width: gridSize * tileSize,
    height: gridSize * tileSize,
    scene: {
        preload,
        create,
        update
    }
};

const game = new Phaser.Game(config);

function preload() {}

function create(data) {

    currentScene = this;

    // If we already have grid data (after upload)

    if (data && data.grid) {

        grid = data.grid;

        spawns = data.spawns;

        drawGrid(this);

        // Player

        player = this.add.rectangle(

            (gridSize / 2) * tileSize,

            (gridSize - 2) * tileSize,

            tileSize,

            tileSize,

            0x00ff00

        );

        // Pathfinding

        const easystar = new EasyStar.js();

        easystar.setGrid(grid);

        easystar.setAcceptableTiles([0]);

        // Spawn enemies

        spawns.forEach(spawn => {

            spawnEnemy(this, spawn, easystar);

        });

    } else {

        // Initial state (before upload)

        this.add.text(50, 50, "Upload an image to start", {

            fontSize: "20px",

            fill: "#ffffff"

        });

    }

}

function update() {}

function drawGrid(scene) {
    for (let y = 0; y < gridSize; y++) {
        for (let x = 0; x < gridSize; x++) {
            let color = grid[y][x] === 1 ? 0x333333 : 0xdddddd;

            scene.add.rectangle(
                x * tileSize,
                y * tileSize,
                tileSize - 1,
                tileSize - 1,
                color
            ).setOrigin(0);
        }
    }
}

function spawnEnemy(scene, spawn, easystar) {
    const enemy = scene.add.rectangle(
        spawn[1]*tileSize,
        spawn[0]*tileSize,
        tileSize,
        tileSize,
        0xff0000
    );

    const targetX = Math.floor(gridSize/2);
    const targetY = gridSize - 2;

    easystar.findPath(
        spawn[1], spawn[0],
        targetX, targetY,
        function(path) {
            if (!path) return;

            moveEnemy(scene, enemy, path);
        }
    );

    easystar.calculate();
}

function moveEnemy(scene, enemy, path) {
    let i = 0;

    scene.time.addEvent({
        delay: 300,
        repeat: path.length - 1,
        callback: () => {
            i++;
            if (path[i]) {
                enemy.x = path[i].x * tileSize;
                enemy.y = path[i].y * tileSize;
            }
        }
    });
}


async function uploadImage() {

    const fileInput = document.getElementById("imageInput");

    const file = fileInput.files[0];

    if (!file) {

        alert("Please select an image!");

        return;

    }

    const formData = new FormData();

    formData.append("file", file);

    const response = await fetch("http://127.0.0.1:8000/scan", {

        method: "POST",

        body: formData

    });

    const data = await response.json();

    console.log("API response:", data);

    // restart scene with new data

    currentScene.scene.restart(data);

}