import cv2
import pygame
from pygame.locals import MOUSEBUTTONDOWN, FULLSCREEN, QUIT
import time
import json

# Initialize Pygame
pygame.init()

# Define screen dimensions and create side window in full-screen mode
info = pygame.display.Info()
main_screen_width, main_screen_height = info.current_w, info.current_h
main_screen = pygame.display.set_mode((main_screen_width, main_screen_height), FULLSCREEN)
pygame.display.set_caption("Face Video Experience")

# Bring the Pygame window to the front
pygame.display.set_mode((main_screen_width, main_screen_height), FULLSCREEN)
pygame.display.flip()

# Define game variables
speed_cm_per_click = 5000
total_distance_cm = 0
max_speed_kph = 0
click_intervals = []
running = False
game_start_time = None
game_duration = 33
result_display_time = 22
last_key_time = None  # Initialize last_key_time
playing_start_video = False
data_displayed = False  # Track if data is displayed

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

current_main_video = main_videos['start']
result_video = cv2.VideoCapture('static/video/face_saver.mp4')

# Load custom font
font_path = 'static/font/JlsdatagothicRnc.otf'
custom_font = pygame.font.Font(font_path, 40)

# Function to switch videos based on click interval
def switch_video(average_interval):
    global current_main_video
    if average_interval < thresholds['288kmph']:
        if current_main_video != main_videos['288kmph']:
            current_main_video = main_videos['288kmph']
            current_main_video.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reset to the first frame
    elif average_interval < thresholds['144kmph']:
        if current_main_video != main_videos['144kmph']:
            current_main_video = main_videos['144kmph']
            current_main_video.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reset to the first frame
    elif average_interval < thresholds['72kmph']:
        if current_main_video != main_videos['72kmph']:
            current_main_video = main_videos['72kmph']
            current_main_video.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reset to the first frame
    else:
        if current_main_video != main_videos['36kmph']:
            current_main_video = main_videos['36kmph']
            current_main_video.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reset to the first frame

def calculate_speed(average_interval):
    # Calculate speed in KM/H based on average click interval
    return (speed_cm_per_click / average_interval) * 0.036

def load_data_from_json():
    with open('records.json', 'r') as file:
        data = json.load(file)
    # Assuming the date key is the current date; you can adjust if needed
    date_key = time.strftime('%Y-%m-%d')
    return data.get(date_key, {'total_distance_cm': 0, 'average_speed_kph': 0})

def display_results():
    end_time = time.time() + result_display_time
    while time.time() < end_time:
        ret_side, frame_side = result_video.read()
        if not ret_side:
            result_video.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret_side, frame_side = result_video.read()

        frame_side = cv2.cvtColor(frame_side, cv2.COLOR_BGR2RGB)
        frame_side = cv2.resize(frame_side, (main_screen_width, main_screen_height))
        frame_side_surface = pygame.surfarray.make_surface(frame_side.swapaxes(0, 1))

        main_screen.fill((0, 0, 0))  # Clear the screen
        main_screen.blit(frame_side_surface, (0, 0))

        # Display total distance text
        result_text_distance = f"{total_distance_cm / 100000:.2f} KM"
        result_lines_distance = result_text_distance.split("\n")
        x_offset_distance = main_screen_width // 2 - 350  # Adjust this value to move the text to the left
        y_offset_distance = main_screen_height // 2 - len(result_lines_distance) * 60  # Adjusted for larger text
        for line in result_lines_distance:
            result_label_distance = custom_font.render(line, True, (255, 255, 255))
            result_label_distance = pygame.transform.rotate(result_label_distance, 270)  # Rotate the text
            main_screen.blit(result_label_distance, (x_offset_distance, y_offset_distance))
            y_offset_distance += 120  # Adjusted for larger text

        # Display average speed text
        result_text_speed = f"{calculate_speed(sum(click_intervals) / len(click_intervals)):.2f} KM/H"
        result_lines_speed = result_text_speed.split("\n")
        x_offset_speed = main_screen_width // 2 - 550  # Move this text further left
        y_offset_speed = main_screen_height // 2 - len(result_lines_speed) * 105  # Same vertical position
        for line in result_lines_speed:
            result_label_speed = custom_font.render(line, True, (255, 255, 255))
            result_label_speed = pygame.transform.rotate(result_label_speed, 270)  # Rotate the text
            main_screen.blit(result_label_speed, (x_offset_speed, y_offset_speed))
            y_offset_speed += 120  # Adjusted for larger text

        pygame.display.flip()
        pygame.time.delay(33)

def display_start_video_data():
    # Load data from JSON
    data = load_data_from_json()
    total_distance_cm = data['total_distance_cm']
    average_speed_kph = data['average_speed_kph']
    
    end_time = time.time() + result_display_time
    while time.time() < end_time:
        ret_main, frame_main = current_main_video.read()
        if not ret_main:
            current_main_video.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret_main, frame_main = current_main_video.read()

        frame_main = cv2.cvtColor(frame_main, cv2.COLOR_BGR2RGB)
        frame_main = cv2.resize(frame_main, (main_screen_width, main_screen_height))
        frame_main_surface = pygame.surfarray.make_surface(frame_main.swapaxes(0, 1))

        main_screen.fill((0, 0, 0))  # Clear the screen
        main_screen.blit(frame_main_surface, (0, 0))

        # Display total distance text
        result_text_distance = f"{total_distance_cm / 100000:.2f} KM"
        result_lines_distance = result_text_distance.split("\n")
        x_offset_distance = main_screen_width // 2 - 320  # Adjust this value to move the text to the left
        y_offset_distance = main_screen_height // 2 - len(result_lines_distance) * 60  # Adjusted for larger text
        for line in result_lines_distance:
            result_label_distance = custom_font.render(line, True, (255, 255, 255))
            result_label_distance = pygame.transform.rotate(result_label_distance, 270)  # Rotate the text
            main_screen.blit(result_label_distance, (x_offset_distance, y_offset_distance))
            y_offset_distance += 120  # Adjusted for larger text

        # Display average speed text
        result_text_speed = f"{average_speed_kph:.2f} KM/H"
        result_lines_speed = result_text_speed.split("\n")
        x_offset_speed = main_screen_width // 2 - 510  # Move this text further left
        y_offset_speed = main_screen_height // 2 - len(result_lines_speed) * 105  # Same vertical position
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
            quit()
        elif event.type == MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                total_distance_cm += speed_cm_per_click
                print(f"Total Distance: {total_distance_cm / 100000:.2f} KM")

                click_time = time.time()
                click_intervals.append(click_time - last_key_time)
                last_key_time = click_time

                if len(click_intervals) > 0:
                    average_interval = sum(click_intervals) / len(click_intervals)
                    speed_kph = calculate_speed(average_interval)
                    max_speed_kph = max(max_speed_kph, speed_kph)
                    switch_video(average_interval)

                print(f"Max Speed: {max_speed_kph:.2f} KM/H")

    if running:
        elapsed_time = time.time() - game_start_time

        if playing_start_video:
            if elapsed_time < 5:
                ret_main, frame_main = current_main_video.read()
                if not ret_main:
                    current_main_video.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    ret_main, frame_main = current_main_video.read()
                frame_main = cv2.cvtColor(frame_main, cv2.COLOR_BGR2RGB)
                frame_main = cv2.resize(frame_main, (main_screen_width, main_screen_height))
                frame_main_surface = pygame.surfarray.make_surface(frame_main.swapaxes(0, 1))

                main_screen.blit(frame_main_surface, (0, 0))
                pygame.display.flip()
            else:
                playing_start_video = False
                current_main_video = main_videos['36kmph']
        elif elapsed_time >= game_duration:
            running = False
            result_video.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reset the result video to the first frame
            display_results()
            total_distance_cm = 0
            max_speed_kph = 0
            click_intervals = []
            data_displayed = False  # Reset the data displayed flag
            current_main_video = main_videos['start']  # Reset to the start video
            playing_start_video = False  # Ensure start video is not playing

        ret_main, frame_main = current_main_video.read()
        if not ret_main:
            current_main_video.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret_main, frame_main = current_main_video.read()

        frame_main = cv2.cvtColor(frame_main, cv2.COLOR_BGR2RGB)
        frame_main = cv2.resize(frame_main, (main_screen_width, main_screen_height))
        frame_main_surface = pygame.surfarray.make_surface(frame_main.swapaxes(0, 1))

        main_screen.blit(frame_main_surface, (0, 0))

        # Display the total distance on the screen
        distance_text = f"{total_distance_cm / 100000:.2f} KM"
        distance_lines = distance_text.split("\n")
        x_offset_distance = main_screen_width // 2 - 500
        y_offset_distance = main_screen_height // 2 - len(distance_lines) * 30
        for line in distance_lines:
            distance_label = custom_font.render(line, True, (255, 255, 255))
            main_screen.blit(distance_label, (x_offset_distance, y_offset_distance))
            y_offset_distance += 60

        # Display the average speed on the screen
        if click_intervals:
            average_speed_text = f"Average Speed: {calculate_speed(sum(click_intervals) / len(click_intervals)):.2f} KM/H"
            speed_lines = average_speed_text.split("\n")
            x_offset_speed = main_screen_width // 2 + 100
            y_offset_speed = main_screen_height // 2 - len(speed_lines) * 30
            for line in speed_lines:
                speed_label = custom_font.render(line, True, (255, 255, 255))
                main_screen.blit(speed_label, (x_offset_speed, y_offset_speed))
                y_offset_speed += 60

        pygame.display.flip()

    if not running and not data_displayed:  # If not running and data not displayed
        display_start_video_data()
        data_displayed = True  # Set the flag to indicate data is displayed
    else:
        ret_main, frame_main = current_main_video.read()
        if not ret_main:
            current_main_video.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret_main, frame_main = current_main_video.read()

        frame_main = cv2.cvtColor(frame_main, cv2.COLOR_BGR2RGB)
        frame_main = cv2.resize(frame_main, (main_screen_width, main_screen_height))
        frame_main_surface = pygame.surfarray.make_surface(frame_main.swapaxes(0, 1))

        main_screen.blit(frame_main_surface, (0, 0))

        pygame.display.flip()

    pygame.time.delay(33)
