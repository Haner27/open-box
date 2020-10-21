from open_box.file.image import Image


def image_usage():
    img = Image('https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1603282675348&di=517865944433fc76b375dc7f2415650c&imgtype=0&src=http%3A%2F%2Fa2.att.hudong.com%2F36%2F48%2F19300001357258133412489354717.jpg')
    print(img.profile)


if __name__ == '__main__':
    image_usage()
