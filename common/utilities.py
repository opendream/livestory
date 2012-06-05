import base64, hashlib, os
import EXIF

from dateutil import parser

from django.conf import settings

def generate_username(email):
    return generate_md5_base64(email)

def generate_md5_base64(str):
    m = hashlib.md5()
    m.update(str)
    hash = base64.urlsafe_b64encode(m.digest())
    hash = hash.replace('=', '')
    hash = hash.replace('+', '-')
    hash = hash.replace('/', '_')

    return hash

def split_filepath(path):
    (head, tail) = os.path.split(path)
    (root, ext) = os.path.splitext(tail)

    if ext and ext[0] == '.':
        ext = ext[1:]

    return (head, root, ext)

def capfirst(text):
    return text and text[0].upper() + text[1:].lower()

def scale_image(image_path, size, method='scale'):
    """
    Return generated or cached thumbnail relative path

    image_path - a full path in file system
    size - an array or tuple of width and height
    """
    (original_path, file_name, file_ext) = split_filepath(image_path)
    cached_filename = '%s.%s.%dx%d_%s.jpg' % (file_name, file_ext, size[0], size[1], method)
    cached_file_path = '%s/%s' % (original_path, cached_filename)

    if not os.path.exists(image_path):
        return False

    if not os.path.exists(cached_file_path):
        try:
            import Image
        except ImportError:
            try:
                from PIL import Image
            except ImportError:
                raise ImportError('Cannot import the Python Image Library.')

        image = Image.open(image_path)

        # normalize image mode
        if image.mode != 'RGBA':
            image = image.convert('RGBA')

        if format == 'PNG':
            pixdata = image.load()
            for y in xrange(image.size[1]):
                for x in xrange(image.size[0]):
                    if pixdata[x, y] == (0, 0, 0, 0):
                        pixdata[x, y] = (255, 255, 255, 0)

        if method == 'scale':
            image.thumbnail(size, Image.ANTIALIAS)
            image.save(cached_file_path, 'JPEG')
        elif method == 'crop':
            try:
                import ImageOps
            except ImportError:
                from PIL import ImageOps

            ImageOps.fit(image, size, Image.ANTIALIAS).save(cached_file_path, 'JPEG', quality=80)

    #return os.path.abspath(cached_file_path).replace(os.path.abspath(settings.BASE_PATH), '')
    return cached_filename

_IMG_MAKE = 'Image Make'
_IMG_MAKE_MODEL = 'Image Model'
_IMG_DATE_ORIGINAL = 'EXIF DateTimeOriginal'

def extract_image_info(img):
    return EXIF.process_file(img) if img else {}

def get_image_captured_date(img):
    data = extract_image_info(img)
    if _IMG_DATE_ORIGINAL in data:
        return parser.parse(str(data[_IMG_DATE_ORIGINAL]))
    else:
        None

def get_image_captured_device(img):
    data = extract_image_info(img)
    device = ''
    if _IMG_MAKE in data:
        device += str(data[_IMG_MAKE])
    if _IMG_MAKE_MODEL in data:
        device += '/' + str(data[_IMG_MAKE_MODEL])
    return device
