from pytube import YouTube
import argparse
from os import path
import os


def download_video(url: str):
    print("downloading video: " + url)
    folderpath = path.join("data", "video")
    video = YouTube(url)
    high_res = video.streams.get_highest_resolution()
    high_res.download(folderpath)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("youtube_url")
    args = parser.parse_args()
    url = args.youtube_url
    download_video(url)
