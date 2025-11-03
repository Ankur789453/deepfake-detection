import os
import cv2

def extract_frames_from_videos(input_folder, output_folder, fps=1):
    """
    Extract frames from all videos in a folder.

    Args:
        input_folder (str): Path to folder containing videos
        output_folder (str): Path to folder to save frames
        fps (int): Frames per second to extract
    """
    os.makedirs(output_folder, exist_ok=True)

    for video_file in os.listdir(input_folder):
        if video_file.endswith((".mp4", ".avi", ".mov", ".mkv")):
            video_path = os.path.join(input_folder, video_file)
            video_name = os.path.splitext(video_file)[0]

            # Create subfolder for each video
            video_output_folder = os.path.join(output_folder, video_name)
            os.makedirs(video_output_folder, exist_ok=True)

            cap = cv2.VideoCapture(video_path)
            frame_rate = int(cap.get(cv2.CAP_PROP_FPS))  # original fps
            frame_interval = max(int(frame_rate / fps), 1)

            count, saved = 0, 0
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                if count % frame_interval == 0:
                    frame_filename = os.path.join(
                        video_output_folder, f"{video_name}_frame_{saved:04d}.jpg"
                    )
                    cv2.imwrite(frame_filename, frame)
                    saved += 1
                count += 1
            cap.release()
            print(f"[DONE] Extracted {saved} frames from {video_file}")

if __name__ == "__main__":
    # Input folders
    real_videos = "data/raw/real"
    fake_videos = "data/raw/fake"

    # Output folders
    real_frames = "data/frames/real_frames"
    fake_frames = "data/frames/fake_frames"

    print("Extracting frames from REAL videos...")
    extract_frames_from_videos(real_videos, real_frames, fps=1)

    print("Extracting frames from FAKE videos...")
    extract_frames_from_videos(fake_videos, fake_frames, fps=1)

    print("✅ All frames extracted successfully!")
