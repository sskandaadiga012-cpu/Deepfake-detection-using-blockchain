import cv2
import os

dataset_path = "dataset/train"
output_path = "frames/train"

classes = ["real", "fake"]

MAX_FRAMES = 10   # limit frames per video

for c in classes:
    video_folder = os.path.join(dataset_path, c)
    save_folder = os.path.join(output_path, c)

    os.makedirs(save_folder, exist_ok=True)

    for video in os.listdir(video_folder):

        # ✅ Improvement 1: handle multiple video formats
        if not video.lower().endswith((".mp4", ".avi", ".mov")):
            continue

        video_path = os.path.join(video_folder, video)
        cap = cv2.VideoCapture(video_path)

        # ✅ Improvement 2: check if video opened properly
        if not cap.isOpened():
            print(f"Skipping {video}, cannot open file")
            continue

        frame_count = 0
        saved_count = 0
        video_name = video.split(".")[0]

        while True:
            ret, frame = cap.read()

            if not ret or saved_count >= MAX_FRAMES:
                break

            # take every 20th frame
            if frame_count % 20 == 0:

                frame_name = f"{video_name}_{saved_count}.jpg"
                frame_path = os.path.join(save_folder, frame_name)

                cv2.imwrite(frame_path, frame)
                saved_count += 1

            frame_count += 1

        cap.release()

print("✅ Frame extraction completed successfully!")