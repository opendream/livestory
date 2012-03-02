import os
import settings

def file_save_upload(f, directory = ''):
    if directory == '':
        directory = '%stemp' % settings.MEDIA_ROOT

    if not os.path.exists(directory):
        os.makedirs(directory)

    filepath = check_file_exists('%s/%s' % (directory, f.name))
    destination = open(filepath, 'wd+')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()

    return { 'filepath': filepath, 'url' : filepath.replace(settings.base_path, '') }

def check_file_exists(filepath, original_filename = '', num_retry = 0):
    num_retry = num_retry + 1
    if os.path.exists(filepath):
        directory, filename = os.path.split(filepath)
        if original_filename == '':
            original_filename = filename
        # TODO handle filename without extension.
        name, ext = original_filename.rsplit('.', 1)
        new_filename = '%s_%s.%s' % (name, num_retry, ext)
        new_filepath = '%s/%s' % (directory, new_filename)
        return check_file_exists(new_filepath, original_filename, num_retry)
    return filepath