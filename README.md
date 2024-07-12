# Virtual Running Game

## Overview
The Virtual Running Game is an interactive and engaging simulation where players can experience a virtual running track through keyboard interactions. The game includes a front-facing video to simulate the runner's view and a side video to enhance realism. The gameplay involves increasing the runner's speed by pressing the right arrow key and running for a total duration of 30 seconds.

## Features
- Front-facing and side-facing video simulations.
- Dynamic video speed adjustments based on player interaction.
- Speed and distance tracking.
- Game duration of 30 seconds with results displayed at the end.
- Custom starting screen with "GET READY... GET SET... AND RUN!" sequence.

## Tech Stack
- **Python**: Core programming language.
- **Pygame**: Used for game development and video playback.
- **OpenCV**: Used for video processing.
- **Custom Font**: JlsdatagothicRnc.otf for in-game text.

## Technical Requirements
- Python 3.x
- Pygame
- OpenCV
- A system capable of running multimedia applications smoothly.

## Setup Instructions
1. **Clone the repository**:
    ```sh
    git clone <repository-url>
    cd <repository-directory>
    ```

2. **Create and activate a virtual environment**:
    ```sh
    python -m venv env
    source env/bin/activate   # On Windows use `env\Scripts\activate`
    ```

3. **Install the required dependencies**:
    ```sh
    pip install -r requirements.txt
    ```

4. **Place the video and font files**:
    - Place your video files in the `static/video` directory.
    - Place your custom font file in the `static/font` directory.

5. **Run the game**:
    ```sh
    python stop_and_go.py
    ```

## Game Rules
1. **Game Start**: 
   - The game starts when the player presses the `space` key.
   - Any other key press before pressing `space` will not start the game.

2. **Gameplay**:
   - The player increases the runner's speed by pressing the `right` arrow key.
   - The player's speed and total distance covered are displayed on the screen.
   - The game runs for a total of 30 seconds.

3. **Game End**:
   - After 30 seconds, the game displays the total distance covered and the maximum speed achieved for 7 seconds.
   - The game then returns to the starting screen, ready for a new session.

## Usage
1. **Game Initialization**:
   - The game begins with a starting screen showing a video with "GET READY... GET SET... AND RUN!".

2. **Running Simulation**:
   - Press the `space` key to start the game.
   - Increase your speed by repeatedly pressing the `right` arrow key.

3. **Viewing Results**:
   - After 30 seconds, view your total distance and maximum speed displayed on the screen for 7 seconds.

4. **Restarting the Game**:
   - After viewing the results, the game returns to the starting screen, ready for another run.

## Notes
- Ensure your system has the necessary hardware to handle video processing for an optimal experience.
- The game speed adjustments are based on the intervals between your key presses, creating a dynamic running experience.

## Contribution
Contributions to the Virtual Running Game are welcome! Feel free to open issues or submit pull requests to enhance the game further.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

Enjoy your virtual running experience!
---

Copyright (c) Ademord Studio 2024
