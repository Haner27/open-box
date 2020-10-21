from PIL import Image as Im

from . import File


class Image(File):
    def __init__(self, input, filename=''):
        super().__init__(input, filename)
        self.im = Im.open(self.bio)
        self.bio.seek(0)
        self.width, self.height = self.im.size
        self.format = self.im.format

    @property
    def profile(self):
        pf = super().profile
        pf.update(width=self.width, height=self.height, format=self.format)
        return pf
