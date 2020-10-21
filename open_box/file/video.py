from tempfile import NamedTemporaryFile

from pymediainfo import MediaInfo

from . import File
from .error import FileInputTypeError
from ..datetime import covert_duration_text


class Video(File):
    def __init__(self, input, filename=''):
        super().__init__(input, filename)
        width, height, duration = self.__get_video_info()
        if not self.content_type.startswith('video'):
            raise FileInputTypeError('Video仅仅支持视频文件输入')
        self.width = width
        self.height = height
        self.duration = duration

    def __get_video_info(self):
        width = 0
        height = 0
        duration = 0

        with NamedTemporaryFile(suffix=self.ext) as f:
            with open(f.name, 'wb') as fi:
                fi.write(self.bio.getvalue())

            self.bio.seek(0)

            media_info = MediaInfo.parse(f.name)
            data = media_info.to_data()
            tracks = data['tracks']
            tracks_video_list = list(filter(lambda a: a['track_type'].lower() == 'video', tracks))
            if tracks_video_list:
                tracks_video = tracks_video_list[0]
                duration = int(float(tracks_video['duration']))
                width = tracks_video['width']
                height = tracks_video['height']
            return width, height, duration

    @property
    def duration_text(self):
        return covert_duration_text(self.duration / 1000)

    @property
    def profile(self):
        pf = super().profile
        pf.update(width=self.width, height=self.height, duration=self.duration, duration_text=self.duration_text)
        return pf