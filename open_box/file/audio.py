from tempfile import NamedTemporaryFile

from pymediainfo import MediaInfo

from . import File
from .error import FileInputTypeError
from ..datetime import covert_duration_text


class Audio(File):
    def __init__(self, input, filename=''):
        super().__init__(input, filename)
        if not self.content_type.startswith('audio'):
            raise FileInputTypeError('Audio仅仅支持音频文件输入')
        duration = self.__get_audio_info()
        self.duration = duration

    def __get_audio_info(self):
        duration = 0

        with NamedTemporaryFile(suffix=self.ext) as f:
            with open(f.name, 'wb') as fi:
                fi.write(self.bio.getvalue())

            self.bio.seek(0)

            media_info = MediaInfo.parse(f.name)
            data = media_info.to_data()
            tracks = data['tracks']
            tracks_audio_list = list(filter(lambda a: a['track_type'].lower() == 'audio', tracks))
            if tracks_audio_list:
                tracks_audio = tracks_audio_list[0]
                duration = tracks_audio['duration']
            return duration

    @property
    def duration_text(self):
        return covert_duration_text(self.duration / 1000)

    @property
    def profile(self):
        pf = super().profile
        pf.update(duration=self.duration, duration_text=self.duration_text)
        return pf