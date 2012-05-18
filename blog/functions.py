import os, uuid

from django.conf import settings

from common.utilities import split_filepath, scale_image

# Blog Image

def save_temporary_blog_image(image_file):
    if not os.path.exists(settings.TEMP_BLOG_IMAGE_ROOT):
        os.makedirs(settings.TEMP_BLOG_IMAGE_ROOT)

    (root, file_name, file_ext) = split_filepath(image_file.name)

    file_name = '%s.%s' % (uuid.uuid4(), file_ext)

    destination = open('%s%s' % (settings.TEMP_BLOG_IMAGE_ROOT, file_name), 'wd+')
    for chunk in image_file.chunks():
        destination.write(chunk)
    destination.close()

    thumbnail_filename = scale_image('%s%s' % (settings.TEMP_BLOG_IMAGE_ROOT, file_name), (settings.BLOG_IMAGE_PREVIEW_WIDTH, settings.BLOG_IMAGE_PREVIEW_HEIGHT))
    thumbnail_url = '%s%s%s' % (settings.MEDIA_URL, settings.TEMP_BLOG_IMAGE_URL, thumbnail_filename)
    return file_name, thumbnail_url

def check_temporary_blog_image(file_name):
    return file_name and os.path.exists('%s/%s' % (settings.TEMP_BLOG_IMAGE_ROOT, file_name))

def remove_temporary_blog_image(file_name):
    if os.path.exists('%s/%s' % (settings.TEMP_BLOG_IMAGE_ROOT, file_name)):
        for f in os.listdir(settings.TEMP_BLOG_IMAGE_ROOT):
            if not f.find(file_name):
                os.remove(os.path.join(settings.TEMP_BLOG_IMAGE_ROOT, f))

def check_blog_image(blog):
    (root, name, ext) = split_filepath(blog.image.path)
    return os.path.exists('%s%s/%s.%s' % (settings.BLOG_IMAGE_ROOT, blog.user.id, name, ext))

def remove_blog_image(blog):
    (root, name, ext) = split_filepath(blog.image.path)
    for f in os.listdir('%s%s/' % (settings.BLOG_IMAGE_ROOT, blog.user.id)):
        if not f.find('%s.%s' % (name, ext)):
            os.remove(os.path.join('%s%s/' % (settings.BLOG_IMAGE_ROOT, blog.user.id), f))
