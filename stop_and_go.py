import pygame
import sys
import time
from moviepy.editor import VideoFileClip

# Initialize Pygame
pygame.init()

# Set up the display
width, height = 400, 800  # Portrait mode dimensions
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Virtual Running Experience")

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Load custom font
custom_font_path = 'XYBER.otf'  # The custom font file name
font_size = 12  # Slightly smaller font size
font = pygame.font.Font(custom_font_path, font_size)

# Load the video
video_path = 'track__25fps_pace3.mp4'  # The updated video file name
video = VideoFileClip(video_path).resize((width, height))

# Initial variables
speed_cm_per_click = 120  # Updated speed parameter
speed_kph = 0
total_distance_cm = 0
is_playing = False
video_start_time = None
pause_time = None
last_key_time = None
playback_speed = 1.0

# Function to convert KPH to MPH
def kph_to_mph(kph):
    return kph * 0.621371

# Function to display speed
def display_speed(screen, speed, total_distance):
    speed_text = font.render(f"Speed: {speed_cm_per_click * speed_kph / 100000:.2f} KM", True, WHITE)
    distance_text = font.render(f"Total: {total_distance / 100000:.2f} KM", True, WHITE)
    screen.blit(speed_text, (10, 10))
    screen.blit(distance_text, (width - 150, 10))  # Adjusted position to be more to the left
    pygame.display.flip()

# Function to display animation
def display_animation(screen):
    animation_text = font.render("You reached another KM!", True, WHITE)
    screen.blit(animation_text, (10, height - 60))
    pygame.display.flip()

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                total_distance_cm += speed_cm_per_click
                speed_kph += 1
                if not is_playing:
                    is_playing = True
                    if pause_time:
                        video_start_time += time.time() - pause_time
                    else:
                        video_start_time = time.time()
                current_time = time.time()
                if last_key_time is not None:
                    elapsed_time = current_time - last_key_time
                    if elapsed_time < 0.5:  # Adjust based on key press speed
                        playback_speed = min(playback_speed + 0.1, 3.0)  # Cap at 3x speed
                    else:
                        playback_speed = max(1.0, playback_speed - 0.1)  # Minimum speed 1x
                last_key_time = current_time
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                is_playing = False
                pause_time = time.time()

    if is_playing:
        current_time = (time.time() - video_start_time) * playback_speed
        frame = video.get_frame(current_time % video.duration)

        # Convert the frame to Pygame surface
        frame = pygame.surfarray.make_surface(frame.swapaxes(0, 1))

        # Display the frame
        screen.blit(frame, (0, 0))

        # Display the speed and total distance on top of the video
        display_speed(screen, speed_kph, total_distance_cm)

        # Display the animation if total distance is every 1 KM
        if total_distance_cm % 100000 < speed_cm_per_click:
            display_animation(screen)

        # Update the display
        pygame.display.flip()
    else:
        # Display the last frame
        if pause_time:
            current_time = (pause_time - video_start_time) * playback_speed
            frame = video.get_frame(current_time % video.duration)

            # Convert the frame to Pygame surface
            frame = pygame.surfarray.make_surface(frame.swapaxes(0, 1))

            # Display the frame
            screen.blit(frame, (0, 0))

            # Display the speed and total distance on top of the video
            display_speed(screen, speed_kph, total_distance_cm)

            # Display the animation if total distance is every 1 KM
            if total_distance_cm % 100000 < speed_cm_per_click:
                display_animation(screen)

            # Update the display
            pygame.display.flip()

pygame.quit()
sys.exit()
