import os
import csv

# Paths where cropped faces are stored
real_dir = "data/tem_faces/real_faces"
fake_dir = "data/tem_faces/fake_faces"

# Output CSV file
csv_file = "data/face_labels.csv"

# Function to gather data
def collect_data(base_dir, label):
    data = []
    for video_id in os.listdir(base_dir):
        video_path = os.path.join(base_dir, video_id)
        if not os.path.isdir(video_path):
            continue
        for frame in os.listdir(video_path):
            if frame.endswith((".jpg", ".png")):
                frame_path = os.path.join(video_path, frame)
                data.append([frame_path, label, video_id])
    return data

# Collect real (label = 0) and fake (label = 1)
real_data = collect_data(real_dir, 0)
fake_data = collect_data(fake_dir, 1)

# Merge both
all_data = real_data + fake_data

# Save to CSV
with open(csv_file, mode="w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["frame_path", "label", "video_id"])
    writer.writerows(all_data)

print(f"✅ CSV file created: {csv_file}")
print(f"Total samples: {len(all_data)}")
