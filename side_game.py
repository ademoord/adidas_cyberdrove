import cv2
import pygame
from pygame.locals import *
import time

# Initialize Pygame
pygame.init()

# Define screen dimensions and create side window
side_screen_width, side_screen_height = 1080, 1920
side_screen = pygame.display.set_mode((side_screen_width, side_screen_height))
pygame.display.set_caption("Side Video Experience")

# Define game variables
speed_cm_per_click = 120
total_distance_cm = 0
max_speed_kph = 0
click_intervals = []
running = False
game_start_time = None
game_duration = 30
result_display_time = 7
last_key_time = None  # Initialize last_key_time

# Define thresholds for switching videos
thresholds = {
    '288kmph': 0.125,  # Example threshold for 288kmph
    '144kmph': 0.25,   # Example threshold for 144kmph
    '72kmph': 0.5,     # Example threshold for 72kmph
    '36kmph': 1.0      # Example threshold for 36kmph
}

# Load the videos using OpenCV
side_videos = {
    '36kmph': cv2.VideoCapture('static/video/side_oAo1_HD_30fps_36kmph.mp4'),
    '72kmph': cv2.VideoCapture('static/video/side_oAo1_HD_30fps_72kmph.mp4'),
    '144kmph': cv2.VideoCapture('static/video/side_oAo1_HD_30fps_144kmph.mp4'),
    '288kmph': cv2.VideoCapture('static/video/side_oAo1_HD_30fps_288kmph.mp4'),
    'start': cv2.VideoCapture('static/video/side_screenSaver.mp4')
}

current_side_video = side_videos['start']

# Load custom font
font_path = 'static/font/JlsdatagothicRnc.otf'
custom_font = pygame.font.Font(font_path, 12)

# Function to switch videos based on click interval
def switch_video(average_interval):
    global current_side_video
    if average_interval < thresholds['288kmph']:
        current_side_video = side_videos['288kmph']
    elif average_interval < thresholds['144kmph']:
        current_side_video = side_videos['144kmph']
    elif average_interval < thresholds['72kmph']:
        current_side_video = side_videos['72kmph']
    else:
        current_side_video = side_videos['36kmph']

# Function to display results
def display_results():
    side_screen.fill((0, 0, 0))  # Clear the screen
    result_text = f"Total Distance: {total_distance_cm / 100000:.2f} KM\nMax Speed: {max_speed_kph:.2f} KM/H"
    result_lines = result_text.split("\n")
    y_offset = side_screen_height // 2 - len(result_lines) * 20
    for line in result_lines:
        result_label = custom_font.render(line, True, (255, 255, 255))
        side_screen.blit(result_label, (side_screen_width // 2 - result_label.get_width() // 2, y_offset))
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
        current_side_video = side_videos['start']

    # Read frame from the current side video
    ret_side, frame_side = current_side_video.read()
    if not ret_side:
        current_side_video.set(cv2.CAP_PROP_POS_FRAMES, 0)
        ret_side, frame_side = current_side_video.read()

    # Convert the side frame to a Pygame surface
    frame_side = cv2.cvtColor(frame_side, cv2.COLOR_BGR2RGB)
    frame_side = cv2.resize(frame_side, (side_screen_width, side_screen_height))
    frame_side_surface = pygame.surfarray.make_surface(frame_side.swapaxes(0, 1))

    # Update the side screen with the current side frame
    side_screen.fill((0, 0, 0))  # Clear the screen
    side_screen.blit(frame_side_surface, (0, 0))

    pygame.display.flip()
    pygame.time.delay(30)
