# encoding:utf-8
#!/usr/bin/env python
from dx_crm import settings
try:
    from PIL import Image, ImageEnhance
except:
    import Image, ImageEnhance
from StringIO import StringIO
from django.core.files.uploadedfile import InMemoryUploadedFile

class Images(object):
    def __init__(self, image, size_dict=settings.IMAGE_SIZE, image_root_path="".join((settings.BASE_DIR,settings.IMAGE_ROOT_PATH)),
                 mark_path=settings.IMAGE_MARK_FILE):
        '''
        初始化程序
        :param image: 图片二进制流
        :param size_dict: 想要改变图片的大小的哈希表
        :param image_root_path: 存放图片根位置
        :param mark_path: 存放水印logo位置
        :return:无
        '''
        import datetime

        self.image = Image.open(image)
        if self.image.mode != 'RGBA':
            self.image = self.image.convert('RGBA')
            self.__img_format = 'JPEG'
        else:
            self.__img_format = 'PNG'
        self.__mark = Image.open(mark_path)
        self.filename = str(image)
        self.__size_dict = size_dict
        self.__root_dir = ''.join((image_root_path, "/", datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")))
        self.__img_dict = {"original_img": self.image}

    def resize(self):
        '''
        按配置改变图片大小
        :return:实例
        '''
        for index in self.__size_dict:
            width_ = int(self.__size_dict[index]['width'])
            height_ = int(self.__size_dict[index]['height'])
            file = self.image.resize((width_, height_), Image.ANTIALIAS)
            self.__img_dict[index] = file
        return self

    def save(self, fileType=None):
        '''
        保存图片到配置位置
        :return:返回地址的hash
        '''
        self.__mkdir()
        path_dict = {}
        if fileType == None or fileType not in self.__img_dict:
            for index in self.__img_dict:
                path = self.__save_to_disk(index)
                path_dict[index] = path
        else:
            path_dict[fileType] = self.__save_to_disk(fileType)

        return path_dict

    def __save_to_disk(self, index):

        path = ''.join((self.__root_dir, "/", str(index) + "/", self.filename))
        self.__img_dict[index].save(path, self.__img_format, quality=100)
        return ''.join((settings.IMAGE_ROOT_PATH,"/", str(index) + "/", self.filename))

    def save_to_memory(self):
        buffer = StringIO()
        self.image.save(buffer, self.__img_format, quality=100)
        self.image = InMemoryUploadedFile(buffer, None, self.filename, self.__img_format, buffer.len, None)
        return self

    def waterMark(self, opacity=1, layout="RIGHT_BOTTOM"):
        '''
        加印水印
        :param opacity:水印图片的透明度
        :param layout: 水印图片在图中的位置
        :return: 实例
        '''
        self.__mark = self.__reduce_opacity(self.__mark, opacity)
        layer = Image.new('RGBA', self.image.size, (0, 0, 0, 0))
        layer.paste(self.__mark, self.__mark_layout(layout))
        image_composite = Image.composite(layer, self.image, layer)
        self.__img_dict["waterMark"] = image_composite
        self.image = image_composite
        return self

    def __reduce_opacity(self, mark, opacity):
        '''
        :param opacity:水印透明度，默认是不透明
        :return: 返回水印图片
        '''
        assert opacity >= 0 and opacity <= 1
        mark = mark.convert('RGBA') if mark.mode != 'RGBA' else mark.copy()
        alpha = mark.split()[3]
        alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
        mark.putalpha(alpha)
        return mark


    def __mkdir(self):
        import os

        os.mkdir(self.__root_dir)
        for index in self.__img_dict:
            path = (self.__root_dir, '/', str(index))
            os.mkdir(''.join(path))


    def __mark_layout(self, layout):
        '''
        :param layout:水印图片位置，默认右下角
        :return:返回相应坐标
        '''

        WIDTH_GRID = 30.0
        HIGHT_GRID = 30.0

        im_width, im_hight = self.image.size[0], self.image.size[1]
        mark_width, mark_hight = self.__mark.size[0], self.__mark.size[1]

        coordinates = {"LEFT_TOP": (int(im_width / WIDTH_GRID), int(im_hight / HIGHT_GRID)),
                       "LEFT_BOTTOM": (int(im_width / WIDTH_GRID), int(im_hight - mark_hight - im_hight / HIGHT_GRID)),
                       "RIGHT_TOP": (int(im_width - mark_width - im_width / WIDTH_GRID), int(im_hight / HIGHT_GRID)),
                       "RIGHT_BOTTOM": (int(im_width - mark_width - im_width / WIDTH_GRID),
                                        int(im_hight - mark_hight - im_hight / HIGHT_GRID)),
        }
        return coordinates[layout]
