from open_box.file.video import Video


def video_usage():
    video = Video('1.mp4')
    print(video.profile)


if __name__ == '__main__':
    video_usage()
