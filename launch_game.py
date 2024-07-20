import subprocess

# Paths to your game scripts
main_game_script = "main_game.py"
side_game_script = "side_game.py"

# Launch the main video game on the primary display in fullscreen
subprocess.Popen(["python", main_game_script, "--display", "0", "--fullscreen"])

# Launch the side video game on the secondary display in fullscreen
subprocess.Popen(["python", side_game_script, "--display", "1", "--fullscreen"])
