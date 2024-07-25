import cv2
import pygame
from pygame.locals import *
import time
import os

# Initialize Pygame
pygame.init()

# Define screen dimensions for both displays
primary_screen_width, screen_height = 1366, 768
extended_screen_width = 1366
combined_screen_width = primary_screen_width + extended_screen_width

# Set the SDL_VIDEO_WINDOW_POS environment variable to position the window at the very left of the primary display
os.environ['SDL_VIDEO_WINDOW_POS'] = f"0,0"

# Create a borderless window that spans both displays
main_screen = pygame.display.set_mode((combined_screen_width, screen_height), NOFRAME)
pygame.display.set_caption("Virtual Running Experience")

# Define game variables
speed_cm_per_click = 120
total_distance_cm = 0
max_speed_kph = 0
click_intervals = []
running = False
game_start_time = None
game_duration = 30
result_display_time = 7

# Define thresholds for switching videos
thresholds = {
    '288kmph': 0.125,  # Example threshold for 288kmph
    '144kmph': 0.25,   # Example threshold for 144kmph
    '72kmph': 0.5,     # Example threshold for 72kmph
    '36kmph': 1.0      # Example threshold for 36kmph
}

# Load the videos using OpenCV
main_videos = {
    '36kmph': cv2.VideoCapture('static/video/face_36.mp4'),
    '72kmph': cv2.VideoCapture('static/video/face_72.mp4'),
    '144kmph': cv2.VideoCapture('static/video/face_144.mp4'),
    '288kmph': cv2.VideoCapture('static/video/face_288.mp4'),
    'start': cv2.VideoCapture('static/video/face_saver.mp4')
}

side_videos = {
    '36kmph': cv2.VideoCapture('static/video/side_36.mp4'),
    '72kmph': cv2.VideoCapture('static/video/side_72.mp4'),
    '144kmph': cv2.VideoCapture('static/video/side_144.mp4'),
    '288kmph': cv2.VideoCapture('static/video/side_288.mp4'),
    'start': cv2.VideoCapture('static/video/side_saver.mp4'),
}

current_main_video = main_videos['start']
current_side_video = side_videos['start']

# Load custom font
font_path = 'static/font/JlsdatagothicRnc.otf'
custom_font = pygame.font.Font(font_path, 12)

# Function to switch videos based on click interval
def switch_video(average_interval):
    global current_main_video, current_side_video
    if average_interval < thresholds['288kmph']:
        current_main_video = main_videos['288kmph']
        current_side_video = side_videos['288kmph']
    elif average_interval < thresholds['144kmph']:
        current_main_video = main_videos['144kmph']
        current_side_video = side_videos['144kmph']
    elif average_interval < thresholds['72kmph']:
        current_main_video = main_videos['72kmph']
        current_side_video = side_videos['72kmph']
    else:
        current_main_video = main_videos['36kmph']
        current_side_video = side_videos['36kmph']

# Function to display results
def display_results():
    main_screen.fill((0, 0, 0))  # Clear the screen
    result_text = f"Total Distance: {total_distance_cm / 100000:.2f} KM\nMax Speed: {max_speed_kph:.2f} KM/H"
    result_lines = result_text.split("\n")
    y_offset = screen_height // 2 - len(result_lines) * 20
    for line in result_lines:
        result_label = custom_font.render(line, True, (255, 255, 255))
        main_screen.blit(result_label, (combined_screen_width // 2 - result_label.get_width() // 2, y_offset))
        y_offset += 40
    pygame.display.flip()
    time.sleep(result_display_time)

# Main loop
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            exit()
        if event.type == KEYDOWN:
            if not running:
                if event.key == K_SPACE:
                    running = True
                    game_start_time = time.time()
                    current_main_video = main_videos['36kmph']
                    current_side_video = side_videos['36kmph']
                    last_key_time = time.time()
                continue
            if event.key == K_RIGHT:
                total_distance_cm += speed_cm_per_click
                current_time = time.time()
                if last_key_time is not None:
                    click_interval = current_time - last_key_time
                    click_intervals.append(click_interval)
                    if len(click_intervals) > 10:  # Keep a rolling average of the last 10 clicks
                        click_intervals.pop(0)
                    average_interval = sum(click_intervals) / len(click_intervals)
                    switch_video(average_interval)  # Switch video based on average click interval
                last_key_time = current_time

    if running and time.time() - game_start_time > game_duration:
        running = False
        display_results()
        total_distance_cm = 0
        max_speed_kph = 0
        click_intervals = []
        current_main_video = main_videos['start']
        current_side_video = side_videos['start']

    # Read frame from the current main video
    ret_main, frame_main = current_main_video.read()
    if not ret_main:
        current_main_video.set(cv2.CAP_PROP_POS_FRAMES, 0)
        ret_main, frame_main = current_main_video.read()

    # Read frame from the current side video
    ret_side, frame_side = current_side_video.read()
    if not ret_side:
        current_side_video.set(cv2.CAP_PROP_POS_FRAMES, 0)
        ret_side, frame_side = current_side_video.read()

    # Convert the main frame to a Pygame surface
    frame_main = cv2.cvtColor(frame_main, cv2.COLOR_BGR2RGB)
    frame_main = cv2.resize(frame_main, (combined_screen_width // 2, screen_height))
    frame_main_surface = pygame.surfarray.make_surface(frame_main.swapaxes(0, 1))

    # Convert the side frame to a Pygame surface
    frame_side = cv2.cvtColor(frame_side, cv2.COLOR_BGR2RGB)
    frame_side = cv2.resize(frame_side, (combined_screen_width // 2, screen_height))
    frame_side_surface = pygame.surfarray.make_surface(frame_side.swapaxes(0, 1))

    # Update the main screen with the current main frame
    main_screen.fill((0, 0, 0))  # Clear the screen
    main_screen.blit(frame_main_surface, (0, 0))

    # Update the side screen with the current side frame
    main_screen.blit(frame_side_surface, (combined_screen_width // 2, 0))

    # Calculate speed
    if click_intervals:
        speed_kph = (speed_cm_per_click / 100) / (sum(click_intervals) / len(click_intervals)) * 3.6
        if speed_kph > max_speed_kph:
            max_speed_kph = speed_kph
    else:
        speed_kph = 0

    if running:
        # Update labels
        speed_text = f"Speed: {speed_kph:.2f} KM/H"
        distance_text = f"Total: {total_distance_cm / 100000:.2f} KM"

        speed_label = custom_font.render(speed_text, True, (255, 255, 255))
        distance_label = custom_font.render(distance_text, True, (255, 255, 255))

        main_screen.blit(speed_label, (10, 10))
        main_screen.blit(distance_label, (combined_screen_width - 140, 10))

    pygame.display.flip()
    pygame.time.delay(30)
