<div align="center">
 <h1>Maze Escape</h1>
 <p><i>A 3D raytracing maze simulation written in python.</i></p>
 <img src="screenshot.png">
</div>

## Requirements & Installation
- This project uses [Python 3](https://www.python.org/download/releases/3.0/), and the [pygame](https://www.pygame.org/wiki/about) library for rendering.
- Installation can be simplified with [homebrew](https://brew.sh/):
```bash
brew install python3
pip install pygame
```
- After that, you can clone the project and navigate to its source directory:
```bash
git clone https://github.com/Camezza/Maze-Escape.git
cd Maze-Escape/src
```

## Usage
- Everything is configured already, so all you need to do is run the program:
```bash
python3 __main__.py
```

## Controls
- Use WASD keys to strafe in cardinal directions.
- Hold SHIFT to sprint.
- Use the ← and → arrow keys to adjust yaw (Look around).

## Objective
- You are stuck at the bottom of a mineshaft and are required to climb 10 progressively harder levels to escape.
- Collect glowing diamonds (blue) to gain extra time (As you stare in awe)
- Collect shiny gold to display the minimap (Gold is conductive, therefore you repair your GPS..?)
- Follow the rainbow light to progress to the next level.
- Keep track of your time. If it runs out, you lose!
