from open_box.file.audio import Audio


def audio_usage():
    audio = Audio('1.mp3')
    print(audio.profile)


if __name__ == '__main__':
    audio_usage()
