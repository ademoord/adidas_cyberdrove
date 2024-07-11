import cv2
import pygame
from pygame.locals import *
import time

# Initialize Pygame
pygame.init()

# Define screen dimensions and create main window
screen_width, screen_height = 800, 600
main_screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Virtual Running Experience")

# Define the speed in centimeters per click
speed_cm_per_click = 120
total_distance_cm = 0
last_key_time = None
click_intervals = []

# Define click interval thresholds
thresholds = {
    '36kmph': 0.5,   # Slower clicks for normal speed
    '72kmph': 0.3,   # Faster clicks for higher speed
    '144kmph': 0.15, # Even faster clicks for higher speed
    '288kmph': 0.075 # Fastest clicks for highest speed
}

# Load the videos using OpenCV
main_videos = {
    '36kmph': cv2.VideoCapture('static/video/track_oBo1_1920X1080_30fps_36kmph.mp4'),
    '72kmph': cv2.VideoCapture('static/video/track_oBo1_1920X1080_30fps_72kmph.mp4'),
    '144kmph': cv2.VideoCapture('static/video/track_oBo1_1920X1080_30fps_144kmph.mp4'),
    '288kmph': cv2.VideoCapture('static/video/track_oBo1_1920X1080_30fps_288kmph.mp4')
}

side_videos = {
    '36kmph': cv2.VideoCapture('static/video/side_oAo1_HD_30fps_36kmph.mp4'),
    '72kmph': cv2.VideoCapture('static/video/side_oAo1_HD_30fps_72kmph.mp4'),
    '144kmph': cv2.VideoCapture('static/video/side_oAo1_HD_30fps_144kmph.mp4'),
    '288kmph': cv2.VideoCapture('static/video/side_oAo1_HD_30fps_288kmph.mp4')
}

current_main_video = main_videos['36kmph']
current_side_video = side_videos['36kmph']

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

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        if event.type == KEYDOWN:
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
    frame_main = cv2.resize(frame_main, (screen_width // 2, screen_height))
    frame_main_surface = pygame.surfarray.make_surface(frame_main.swapaxes(0, 1))

    # Convert the side frame to a Pygame surface
    frame_side = cv2.cvtColor(frame_side, cv2.COLOR_BGR2RGB)
    frame_side = cv2.resize(frame_side, (screen_width // 2, screen_height))
    frame_side_surface = pygame.surfarray.make_surface(frame_side.swapaxes(0, 1))

    # Update the main screen with the current main frame
    main_screen.fill((0, 0, 0))  # Clear the screen
    main_screen.blit(frame_main_surface, (0, 0))

    # Update the side screen with the current side frame
    main_screen.blit(frame_side_surface, (screen_width // 2, 0))

    # Calculate speed
    if click_intervals:
        speed_kph = (speed_cm_per_click / 100) / (sum(click_intervals) / len(click_intervals)) * 3.6
    else:
        speed_kph = 0

    # Update labels
    speed_text = f"Speed: {speed_kph:.2f} KM/H"
    distance_text = f"Total: {total_distance_cm / 100000:.2f} KM"

    speed_label = custom_font.render(speed_text, True, (255, 255, 255))
    distance_label = custom_font.render(distance_text, True, (255, 255, 255))

    main_screen.blit(speed_label, (10, 10))
    main_screen.blit(distance_label, (screen_width - 140, 10))

    pygame.display.flip()
    pygame.time.delay(30)

pygame.quit()
