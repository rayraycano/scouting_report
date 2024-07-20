import cv2
import math
import argparse
from os import path
import os
import base64


def materialize_video(video_name, total_frames):
    if not math.sqrt(total_frames).is_integer():
        raise Exception("requires perfect square number of frames")
    grid_n = int(math.sqrt(total_frames))
    filepath = path.join("data", "video", video_name)
    video = cv2.VideoCapture(filepath)
    frames = []
    try:
        iter = 0
        while video.isOpened():

            success, frame = video.read()
            if not success:
                break
            iter += 1
            frames.append(frame)
        if len(frames) == 0:
            print("no frames; exiting")
            return
        skip_by = len(frames) / total_frames
        sampled_frames = [frames[int(i * skip_by)] for i in range(total_frames)]
        result_image = None
        for row_idx in range(grid_n):
            row_img = None
            for column_idx in range(grid_n):
                total_idx = row_idx * grid_n + column_idx
                if row_img is None:
                    row_img = sampled_frames[total_idx]
                else:
                    row_img = cv2.hconcat([row_img, sampled_frames[total_idx]])
            if result_image is None:
                result_image = row_img
            else:
                result_image = cv2.vconcat([result_image, row_img])
        print(result_image.shape)
        video_filename = video_name.split(".")[0]
        folderpath = path.join("data", "video", "stills", video_filename)
        if not path.exists(folderpath):
            os.makedirs(folderpath)
        filepath = path.join("data", "video", "stills", video_filename, "summary.jpg")
        cv2.imwrite(filepath, result_image)
        for idx, frame in enumerate(frames):
            filepath = path.join(
                "data", "video", "stills", video_filename, f"{idx}.jpg"
            )
            cv2.imwrite(filepath, frame)
        print(f"wrote image: {filepath}")

    finally:
        video.release()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("video_name")
    parser.add_argument("total_frames", type=int)
    args = parser.parse_args()
    materialize_video(args.video_name, args.total_frames)
