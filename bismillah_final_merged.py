import cv2
import pygame
from pygame.locals import MOUSEBUTTONDOWN, FULLSCREEN, QUIT, NOFRAME
import time
import os
import json

# Initialize Pygame
pygame.init()

# Define screen dimensions for both displays
primary_screen_width, screen_height = 1920, 1080
# primary_screen_width, screen_height = 1366, 768
extended_screen_width = 1920
# extended_screen_width = 1366
combined_screen_width = primary_screen_width + extended_screen_width

# Set the SDL_VIDEO_WINDOW_POS environment variable to position the window at the very left of the primary display
os.environ['SDL_VIDEO_WINDOW_POS'] = f"0,0"

# Create a borderless window that spans both displays
main_screen = pygame.display.set_mode((combined_screen_width, screen_height), NOFRAME)
pygame.display.set_caption("Virtual Running Experience")

# Define game variables
speed_cm_per_click = 5000
total_distance_cm = 0
max_speed_kph = 0
click_intervals = []
running = False
game_start_time = None
game_duration = 33
result_display_time = 7
last_key_time = None  # Initialize last_key_time
playing_start_video = False
data_displayed = False  # Track if data is displayed

# Countdown timer variables
countdown_time = 49  # Start with 30 seconds countdown
countdown_start_time = None

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
    'start': cv2.VideoCapture('static/video/face_saver.mp4'),
    'track_start': cv2.VideoCapture('static/video/face_start.mp4'),
    'track_finish': cv2.VideoCapture('static/video/face_finish.mp4')
}


side_videos = {
    '36kmph': cv2.VideoCapture('static/video/side_36.mp4'),
    '72kmph': cv2.VideoCapture('static/video/side_72.mp4'),
    '144kmph': cv2.VideoCapture('static/video/side_144.mp4'),
    '288kmph': cv2.VideoCapture('static/video/side_288.mp4'),
    'start': cv2.VideoCapture('static/video/side_saver.mp4'),
    'track_start': cv2.VideoCapture('static/video/side_start.mp4'),
    'track_finish': cv2.VideoCapture('static/video/side_finish.mp4')
}

current_main_video = main_videos['start']
current_side_video = side_videos['start']
result_main_video = cv2.VideoCapture('static/video/face_saver.mp4')
result_side_video = cv2.VideoCapture('static/video/side_saver.mp4')

# Load custom font
font_path = 'static/font/JlsdatagothicRnc.otf'
custom_font = pygame.font.Font(font_path, 50)

# Function to switch videos based on click interval
def switch_video(average_interval):
    global current_main_video, current_side_video
    if average_interval < thresholds['288kmph']:
        current_main_video = main_videos['288kmph']
        current_side_video = side_videos['288kmph']
    elif average_interval < thresholds['144kmph']:
        current_main_video = main_videos['144kmph']
        current_side_video = side_videos['144kmph']
    else:
        current_main_video = main_videos['72kmph']
        current_side_video = side_videos['72kmph']
    # else:
    #     current_main_video = main_videos['36kmph']
    #     current_side_video = side_videos['36kmph']

# def switch_video(average_interval):
#     global current_main_video, current_side_video
#     if average_interval < thresholds['288kmph']:
#         current_main_video = main_videos['288kmph']
#         current_side_video = side_videos['288kmph']
#     elif average_interval < thresholds['144kmph']:
#         current_main_video = main_videos['144kmph']
#         current_side_video = side_videos['144kmph']
#     elif average_interval < thresholds['72kmph']:
#         current_main_video = main_videos['72kmph']
#         current_side_video = side_videos['72kmph']
#     else:
#         current_main_video = main_videos['36kmph']
#         current_side_video = side_videos['36kmph']


def calculate_speed(average_interval):
    # Calculate speed in KM/H based on average click interval
    return (speed_cm_per_click / average_interval) * 0.036

# def load_data_from_json():
#     try:
#         with open('records.json', 'r') as file:
#             data = json.load(file)
#         # Assuming the date key is the current date; you can adjust if needed
#         date_key = time.strftime('%Y-%m-%d')
#         return data.get(date_key, {'total_distance_cm': 0, 'average_speed_kph': 0})
#     except FileNotFoundError:
#         print("File not found.")
#         data = {}

def load_data_from_json():
    try:
        with open('records.json', 'r') as file:
            data = json.load(file)
        # Get any existing data regardless of the date
        if data:
            return next(iter(data.values()))
        else:
            return {'total_distance_cm': 53.7, 'average_speed_kph': 39400.45}
    except FileNotFoundError:
        print("File not found.")
        return {'total_distance_cm': 53.7, 'average_speed_kph': 39400.45}

def display_results():
    end_time = time.time() + result_display_time
    while time.time() < end_time:
        ret_main, frame_main = result_main_video.read()
        if not ret_main:
            result_main_video.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret_main, frame_main = result_main_video.read() 

        frame_main = cv2.cvtColor(frame_main, cv2.COLOR_BGR2RGB)
        frame_main = cv2.resize(frame_main, (primary_screen_width, screen_height))
        frame_main_surface = pygame.surfarray.make_surface(frame_main.swapaxes(0, 1))

        main_screen.fill((0, 0, 0))  # Clear the screen
        main_screen.blit(frame_side_surface, (0, 0))

        # Display total distance text
        result_text_distance = f"{total_distance_cm / 100000:.2f} KM"
        result_lines_distance = result_text_distance.split("\n")
        x_offset_distance = primary_screen_width // 2 - 350  # Adjust this value to move the text to the left
        y_offset_distance = screen_height // 2 - len(result_lines_distance) * 60  # Adjusted for larger text
        for line in result_lines_distance:
            result_label_distance = custom_font.render(line, True, (255, 255, 255))
            result_label_distance = pygame.transform.rotate(result_label_distance, 270)  # Rotate the text
            main_screen.blit(result_label_distance, (x_offset_distance, y_offset_distance))
            y_offset_distance += 120  # Adjusted for larger text

        # Display average speed text
        if click_intervals:  # Check if click_intervals is not empty
            average_interval = sum(click_intervals) / len(click_intervals)
            result_text_speed = f"{calculate_speed(average_interval):.2f} KM/H"
        else:
            result_text_speed = "Speed: 0.00 KM/H"  # Default value if no intervals are available

        result_lines_speed = result_text_speed.split("\n")
        x_offset_speed = primary_screen_width // 2 - 650  # Move this text further left
        y_offset_speed = screen_height // 2 - len(result_lines_speed) * 105  # Same vertical position
        for line in result_lines_speed:
            result_label_speed = custom_font.render(line, True, (255, 255, 255))
            result_label_speed = pygame.transform.rotate(result_label_speed, 270)  # Rotate the text
            main_screen.blit(result_label_speed, (x_offset_speed, y_offset_speed))
            y_offset_speed += 120  # Adjusted for larger text

        pygame.display.flip()
        pygame.time.delay(33)

def display_start_video_data():
    countdown_time = 30  # Start with 30 seconds countdown
    countdown_start_time = None

    # Load data from JSON
    data = load_data_from_json()
    total_distance_cm = data['total_distance_cm']
    average_speed_kph = data['average_speed_kph']
    
    end_time = time.time() + result_display_time
    while time.time() < end_time:
        # Read and process main and side video frames
        ret_main, frame_main = current_main_video.read()
        ret_side, frame_side = current_side_video.read()

        if not ret_main or not ret_side:
            if not ret_main:
                current_main_video.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret_main, frame_main = current_main_video.read()
            if not ret_side:
                current_side_video.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret_side, frame_side = current_side_video.read()

        # Convert frames to Pygame surfaces
        frame_main = cv2.cvtColor(frame_main, cv2.COLOR_BGR2RGB)
        frame_main = cv2.resize(frame_main, (primary_screen_width, screen_height))
        frame_main_surface = pygame.surfarray.make_surface(frame_main.swapaxes(0, 1))

        frame_side = cv2.cvtColor(frame_side, cv2.COLOR_BGR2RGB)
        frame_side = cv2.resize(frame_side, (combined_screen_width // 2, screen_height))
        frame_side_surface = pygame.surfarray.make_surface(frame_side.swapaxes(0, 1))

        # Clear the screen
        main_screen.fill((0, 0, 0))
        
        # Display main video
        main_screen.blit(frame_main_surface, (0, 0))
        
        # Display side video
        main_screen.blit(frame_side_surface, (primary_screen_width, 0))

        # Display total distance text
        result_text_distance = f"{total_distance_cm / 100000:.2f} KM"
        result_lines_distance = result_text_distance.split("\n")
        x_offset_distance = primary_screen_width // 2 - 355  # Adjust this value to move the text to the left
        y_offset_distance = screen_height // 2 - len(result_lines_distance) * 80  # Adjusted for larger text
        for line in result_lines_distance:
            result_label_distance = custom_font.render(line, True, (255, 255, 255))
            result_label_distance = pygame.transform.rotate(result_label_distance, 270)  # Rotate the text
            main_screen.blit(result_label_distance, (x_offset_distance, y_offset_distance))
            y_offset_distance += 120  # Adjusted for larger text

        # Display average speed text
        result_text_speed = f"{average_speed_kph:.2f} KM/H"
        result_lines_speed = result_text_speed.split("\n")
        x_offset_speed = primary_screen_width // 2 - 615  # Move this text further left
        y_offset_speed = screen_height // 2 - len(result_lines_speed) * 115  # Same vertical position
        for line in result_lines_speed:
            result_label_speed = custom_font.render(line, True, (255, 255, 255))
            result_label_speed = pygame.transform.rotate(result_label_speed, 270)  # Rotate the text
            main_screen.blit(result_label_speed, (x_offset_speed, y_offset_speed))
            y_offset_speed += 120  # Adjusted for larger text

        pygame.display.flip()
        pygame.time.delay(33)

# Main loop
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            exit()
        if event.type == MOUSEBUTTONDOWN:
            if not running:
                if event.button == 3:  # Right mouse button
                    running = True
                    game_start_time = time.time()
                    current_main_video = main_videos['track_start']
                    current_side_video = side_videos['track_start']
                    # playing_start_video = True
                    last_key_time = time.time()
                continue

            if event.button == 1:  # Left mouse button
                total_distance_cm += speed_cm_per_click
                total_distance_km = total_distance_cm / 100000  # Convert to kilometers
                current_time = time.time()
                if last_key_time is not None:
                    click_interval = current_time - last_key_time
                    click_intervals.append(click_interval)
                    # if len(click_interval) > 10:
                    if click_interval > 10:
                        click_intervals.pop(0)
                    average_interval = sum(click_intervals) / len(click_intervals)
                    switch_video(average_interval)
                last_key_time = current_time

    if running and time.time() - game_start_time > game_duration:
        running = False
        display_results()
        total_distance_cm = 0
        max_speed_kph = 0
        click_intervals = []
        current_main_video = main_videos['start']
        current_side_video = main_videos['start']

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

    # Convert the main frame to Pygame surfaces
    frame_main = cv2.cvtColor(frame_main, cv2.COLOR_BGR2RGB)
    frame_main = cv2.resize(frame_main, (combined_screen_width // 2, screen_height))
    frame_main_surface = pygame.surfarray.make_surface(frame_main.swapaxes(0, 1))

    # Convert the side frame to Pygame surfaces
    frame_side = cv2.cvtColor(frame_side, cv2.COLOR_BGR2RGB)
    frame_side = cv2.resize(frame_side, (combined_screen_width // 2, screen_height))
    frame_side_surface = pygame.surfarray.make_surface(frame_side.swapaxes(0, 1))

    # Update the main screen with the current main frame
    main_screen.fill((0, 0, 0))  # Clear the screen
    main_screen.blit(frame_main_surface, (0, 0))
    main_screen.blit(frame_side_surface, (combined_screen_width // 2, 0))
           
    # Display speed and distance
    if click_intervals:
        speed_kph = (speed_cm_per_click / 1000) / (sum(click_intervals) / len(click_intervals)) * 3.6
        if speed_kph > max_speed_kph:
            max_speed_kph = speed_kph
    else:
        speed_kph = 0
        
    # Display countdown timer
    if countdown_start_time is None:
        countdown_start_time = time.time()
    elapsed_time = time.time() - countdown_start_time
    remaining_time = max(0, int(countdown_time - elapsed_time))

    if running:
        # Update labels
        speed_text = f"{speed_kph:.2f} KM/H"
        lines_speed = speed_text.split("\n")
        x_offset_speed = primary_screen_width // 2 - 350  # Adjust this value to move the text to the left
        y_offset_speed = screen_height // 2 - len(lines_speed) * 60  # Adjusted for larger text
        for line in lines_speed:
            label_speed = custom_font.render(line, True, (255, 255, 255))
            label_speed = pygame.transform.rotate(label_speed, 270)  # Rotate the text
            main_screen.blit(label_speed, (x_offset_speed, y_offset_speed))
            y_offset_speed += 120  # Adjusted for larger text

        countdown_text = f"{remaining_time}s"
        lines_countdown = countdown_text.split("\n")
        x_offset_countdown = primary_screen_width // 2 + 350  # Adjust this value to move the text to the right
        y_offset_countdown = screen_height // 2 - len(lines_speed) * 60  # Adjusted for larger text
        for line in lines_countdown:
            label_countdown = custom_font.render(line, True, (255, 255, 255))
            label_countdown = pygame.transform.rotate(label_countdown, 270)  # Rotate the text
            main_screen.blit(label_countdown, (x_offset_countdown, y_offset_countdown))
            y_offset_countdown += 650 

        # Calculate center positions
        x_center = primary_screen_width // 2
        y_center = screen_height // 2

        # Adjust these offsets to move the text left or right
        horizontal_offset = 350
        vertical_offset = 0

        pygame.display.flip()

        if not running and not data_displayed:
            display_start_video_data()
            data_displayed = True
    else:
        # Display start video data if not running and data not displayed
        display_start_video_data()
        data_displayed = True

    pygame.time.delay(33)

    # Record the data and replace the existing data in records.json
    data_to_save = {
        'total_distance_cm': total_distance_cm,
        'average_speed_kph': max_speed_kph
    }
    with open('records.json', 'w') as file:
        json.dump(data_to_save, file)