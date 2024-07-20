import os
import pygame
import cv2
import time
import json
import datetime
from pygame.locals import QUIT, FULLSCREEN, MOUSEBUTTONDOWN
from moviepy.editor import VideoFileClip

# Set the SDL_AUDIODRIVER environment variable to pulseaudio
os.environ["SDL_AUDIODRIVER"] = "pulseaudio"

# Initialize Pygame
pygame.init()
pygame.mixer.init()

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

# Define thresholds for switching videos
thresholds = {
    '288kmph': 0.125,  # Example threshold for 288kmph
    '144kmph': 0.25,   # Example threshold for 144kmph
    '72kmph': 0.5,     # Example threshold for 72kmph
    '36kmph': 1.0      # Example threshold for 36kmph
}

# Load the videos using OpenCV
main_videos = {
    '36kmph': cv2.VideoCapture('static/video/track_oBo1_1920X1080_30fps_36kmph.mp4'),
    '72kmph': cv2.VideoCapture('static/video/track_oBo1_1920X1080_30fps_72kmph.mp4'),
    '144kmph': cv2.VideoCapture('static/video/track_oBo1_1920X1080_30fps_144kmph.mp4'),
    '288kmph': cv2.VideoCapture('static/video/track_oBo1_1920X1080_30fps_288kmph.mp4'),
    'start': cv2.VideoCapture('static/video/Face_ScreenSaver.mp4'),
    'track_start': cv2.VideoCapture('static/video/track_Start.mp4'),
    'track_finish': cv2.VideoCapture('static/video/track_Finish.mp4')
}

current_main_video = main_videos['start']
result_video = cv2.VideoCapture('static/video/Face_ScreenSaver.mp4')

# Load the audio using MoviePy
main_audio_clips = {
    '36kmph': VideoFileClip('static/video/track_oBo1_1920X1080_30fps_36kmph.mp4').audio,
    '72kmph': VideoFileClip('static/video/track_oBo1_1920X1080_30fps_72kmph.mp4').audio,
    '144kmph': VideoFileClip('static/video/track_oBo1_1920X1080_30fps_144kmph.mp4').audio,
    '288kmph': VideoFileClip('static/video/track_oBo1_1920X1080_30fps_288kmph.mp4').audio,
    'start': VideoFileClip('static/video/Face_ScreenSaver.mp4').audio,
    'track_start': VideoFileClip('static/video/track_Start.mp4').audio,
    'track_finish': VideoFileClip('static/video/track_Finish.mp4').audio
}

current_main_audio = main_audio_clips['start']

# Load custom font
font_path = 'static/font/JlsdatagothicRnc.otf'
custom_font = pygame.font.Font(font_path, 40)

# Function to switch videos based on click interval
def switch_video(average_interval):
    global current_main_video, current_main_audio
    if average_interval < thresholds['288kmph']:
        current_main_video = main_videos['288kmph']
        current_main_audio = main_audio_clips['288kmph']
    elif average_interval < thresholds['144kmph']:
        current_main_video = main_videos['144kmph']
        current_main_audio = main_audio_clips['144kmph']
    elif average_interval < thresholds['72kmph']:
        current_main_video = main_videos['72kmph']
        current_main_audio = main_audio_clips['72kmph']
    else:
        current_main_video = main_videos['36kmph']
        current_main_audio = main_audio_clips['36kmph']
    play_audio(current_main_audio)

def calculate_speed(average_interval):
    return (speed_cm_per_click / average_interval) * 0.036

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
        x_offset_distance = main_screen_width // 2 - 270  # Adjust this value to move the text to the left
        y_offset_distance = main_screen_height // 2 - len(result_lines_distance) * 60  # Adjusted for larger text
        for line in result_lines_distance:
            result_label_distance = custom_font.render(line, True, (255, 255, 255))
            result_label_distance = pygame.transform.rotate(result_label_distance, 270)  # Rotate the text
            main_screen.blit(result_label_distance, (x_offset_distance, y_offset_distance))
            y_offset_distance += 120  # Adjusted for larger text

        # Display average speed text
        result_text_speed = f"{calculate_speed(sum(click_intervals) / len(click_intervals)):.2f} KM/H"
        result_lines_speed = result_text_speed.split("\n")
        x_offset_speed = main_screen_width // 2 - 460  # Move this text further left
        y_offset_speed = main_screen_height // 2 - len(result_lines_speed) * 105  # Same vertical position
        for line in result_lines_speed:
            result_label_speed = custom_font.render(line, True, (255, 255, 255))
            result_label_speed = pygame.transform.rotate(result_label_speed, 270)  # Rotate the text
            main_screen.blit(result_label_speed, (x_offset_speed, y_offset_speed))
            y_offset_speed += 120  # Adjusted for larger text

        pygame.display.flip()
        pygame.time.delay(33)

def play_audio(audio_clip):
    audio_file = 'temp_audio.wav'
    audio_clip.write_audiofile(audio_file)
    pygame.mixer.music.load(audio_file)
    pygame.mixer.music.play()

def stop_audio():
    pygame.mixer.music.stop()

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
                    current_main_audio = main_audio_clips['track_start']
                    playing_start_video = True
                    last_key_time = time.time()
                    play_audio(current_main_audio)
                continue
            if event.button == 1 and not playing_start_video:  # Left mouse button
                total_distance_cm += speed_cm_per_click
                total_distance_km = total_distance_cm / 100000  # Convert to kilometers
                print(f"Total Distance: {total_distance_km:.2f} KM")  # Print in kilometers
                
                current_time = time.time()
                if last_key_time is not None:
                    click_interval = current_time - last_key_time
                    click_intervals.append(click_interval)
                    if len(click_intervals) > 10:  # Keep a rolling average of the last 10 clicks
                        click_intervals.pop(0)
                    average_interval = sum(click_intervals) / len(click_intervals)
                    average_speed_kph = calculate_speed(average_interval)
                    print(f"Average Speed: {average_speed_kph:.2f} KM/H")  # Print average speed in KM/H
                    switch_video(average_interval)
                last_key_time = current_time

    ret, frame_main = current_main_video.read()
    if not ret:
        current_main_video.set(cv2.CAP_PROP_POS_FRAMES, 0)
        ret, frame_main = current_main_video.read()

    frame_main = cv2.cvtColor(frame_main, cv2.COLOR_BGR2RGB)
    frame_main = cv2.resize(frame_main, (main_screen_width, main_screen_height))
    frame_main_surface = pygame.surfarray.make_surface(frame_main.swapaxes(0, 1))

    main_screen.fill((0, 0, 0))  # Clear the screen
    main_screen.blit(frame_main_surface, (0, 0))

    pygame.display.flip()

    if running and (time.time() - game_start_time) >= game_duration:
        running = False
        stop_audio()
        current_main_video = main_videos['track_finish']
        current_main_audio = main_audio_clips['track_finish']
        play_audio(current_main_audio)
        display_results()
        stop_audio()
        current_main_video = main_videos['start']
        current_main_audio = main_audio_clips['start']
        total_distance_cm = 0
        max_speed_kph = 0
        click_intervals = []

        # Save total distance and average speed to JSON file
        records = {}
        try:
            with open('records.json', 'r') as f:
                records = json.load(f)
        except FileNotFoundError:
            pass

        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        records[current_date] = {
            'total_distance_cm': total_distance_cm,
            'average_speed_kph': average_speed_kph
        }

        with open('records.json', 'w') as f:
            json.dump(records, f, indent=4)

    pygame.time.delay(33)