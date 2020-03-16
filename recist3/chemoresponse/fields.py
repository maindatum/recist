from django.db.models.fields.files import ImageField, ImageFieldFile
from PIL import Image
from django.conf import settings
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEDIA_ROOT = os.path.join(BASE_DIR,'media')

def _add_path_to_thumb(s):
    print('this is path',s)
    fname_list=[]
    parts = s.split(".")
    print('this is parts',parts)
    pathparts=parts[0].split("\\")
    print('this is pathparts', pathparts)
    fname_list.append(pathparts[-1])
    fname_list.append('-thumb')
    fname_list.append('.jpg')
    fname ="".join(fname_list)
    del pathparts[-1]
    pathparts.extend(['thumbnails\\'])
    print('this is pathparts final', pathparts)
    path_prop = "\\".join(pathparts)
    print('this is pathparts final prop', path_prop)
    MEDIA_ROOT_THUMB = os.path.join(MEDIA_ROOT, 'target_image/thumbnails/')
    print('this is media_root_thumb', MEDIA_ROOT_THUMB)
    fullopathusingos = os.path.join(MEDIA_ROOT_THUMB,fname)
    print('this is full path using os ',fullopathusingos )

    fullpath = path_prop+fname
    return fullopathusingos

def _add_url_to_thumb(s):
    print('this is url',s)
    fname_list=[]
    parts = s.split(".")
    pathparts=parts[0].split("/")
    fname_list.append(pathparts[-1])
    fname_list.append('-thumb')
    fname_list.append('.jpg')
    fname ="".join(fname_list)
    del pathparts[-1]
    pathparts.append('thumbnails/')
    path_prop = "/".join(pathparts)
    fullpath = path_prop+fname
    return fullpath


def _add_relpath_to_thumb(nm):
    print('this is nm',nm)
    parts = nm.split("/")[1].split(".")
    parts.insert(-1, '-thumb')
    print('this is parts', parts)
    if parts[-1].lower not in ['jpeg', 'jpg']:
        parts[-1] = '.jpg'
    fname = "".join(parts)
    MEDIA_ROOT_THUMB = os.path.join(MEDIA_ROOT, 'thumbnails')
    fullpath = os.path.join(MEDIA_ROOT_THUMB,fname)
    return fullpath


def _add_relpath_to_thumb2(nm):
    print('this is nm',nm)
    parts = nm.split("/")[1].split(".")
    parts.insert(-1, '-thumb')
    print('this is parts', parts)
    if parts[-1].lower not in ['jpeg', 'jpg']:
        parts[-1] = '.jpg'
    fname = "".join(parts)
    MEDIA_ROOT_THUMB = os.path.join(MEDIA_ROOT, 'thumbnails')
    fullpath = os.path.join(MEDIA_ROOT_THUMB,fname)
    return fullpath


class ImageWithThumbFieldFile(ImageFieldFile):
    def _get_thumb_path(self):
        return _add_path_to_thumb(self.path)
    thumb_path = property(_get_thumb_path)

    def _get_thumb_name(self):
        return self.name
    thumb_name = property(_get_thumb_name)

    def _get_thumb_relpath(self):
        return _add_relpath_to_thumb(self.thumb_name)
    thumb_relpath = property(_get_thumb_relpath)

    def _get_thumb_url(self):
        return _add_url_to_thumb(self.url)
    thumb_url = property(_get_thumb_url)

    def _get_thumb_relurl(self):
        return _add_relpath_to_thumb(self.url)
    thumb_relurl = property(_get_thumb_relurl)


    def save(self, name, content, save=True):
        super(ImageWithThumbFieldFile, self).save(name, content, save)
        print('this is thumb_name',self.thumb_name)
        print('this is name of file', self.field.name)
        print('this is name of self', self.name)
        img = Image.open(self.path)
        size = (128, 128)
        img.thumbnail(size, Image.ANTIALIAS)
        background = Image.new('RGB', size, (255, 255, 255, 0))
        background.paste(
            img, (int((size[0] - img.size[0]) / 2), int((size[1] - img.size[1]) / 2))
                  )
        background.save(self.thumb_path, 'JPEG')

class ImageWithThumbField(ImageField):
    attr_class = ImageWithThumbFieldFile

    def __init__(self, thumb_width=128, thumb_height=128, *args, **kwargs):
        self.thumb_width = thumb_width
        self.thumb_height = thumb_height
        super(ImageWithThumbField, self).__init__(*args, **kwargs)
