# -*- coding: utf-8 -*-
import ast
from flask import current_app
from flask_admin.form.upload import (
    ImageUploadField,
    FileUploadField,
    ImageUploadInput,
    FileUploadInput,
    namegen_filename,
    thumbgen_filename)
from flask_admin.helpers import get_url
from flask_admin._compat import string_types, urljoin
from flask_babelex import lazy_gettext as __
from wtforms import ValidationError
from wtforms.widgets import HTMLString, html_params
try:
    from wtforms.fields.core import _unset_value as unset_value
except ImportError:
    from wtforms.utils import unset_value

try:
    from PIL import Image, ImageOps
except ImportError:
    Image = None
    ImageOps = None


class DropImageUploadInput(ImageUploadInput):
    empty_template = ('<input %(file)s>')


class DropImageUploadField(ImageUploadField):

    widget = DropImageUploadInput()

    def __init__(self, label=None, validators=None,
                 base_path=None, relative_path=None,
                 namegen=None, allowed_extensions=None,
                 max_size=None,
                 thumbgen=None, thumbnail_size=None,
                 permission=0o666,
                 url_relative_path=None, endpoint=None,
                 **kwargs):
        """
            Constructor.
            :param label:
                Display label
            :param validators:
                Validators
            :param base_path:
                Absolute path to the directory which will store files
            :param relative_path:
                Relative path from the directory. Will be prepended to the file name for uploaded files.
                Flask-Admin uses `urlparse.urljoin` to generate resulting filename, so make sure you have
                trailing slash.
            :param namegen:
                Function that will generate filename from the model and uploaded file object.
                Please note, that model is "dirty" model object, before it was committed to database.
                For example::
                    import os.path as op
                    def prefix_name(obj, file_data):
                        parts = op.splitext(file_data.filename)
                        return secure_filename('file-%s%s' % parts)
                    class MyForm(BaseForm):
                        upload = FileUploadField('File', namegen=prefix_name)
            :param allowed_extensions:
                List of allowed extensions. If not provided, then gif, jpg, jpeg, png and tiff will be allowed.
            :param max_size:
                Tuple of (width, height, force) or None. If provided, Flask-Admin will
                resize image to the desired size.
                Width and height is in pixels. If `force` is set to `True`, will try to fit image into dimensions and
                keep aspect ratio, otherwise will just resize to target size.
            :param thumbgen:
                Thumbnail filename generation function. All thumbnails will be saved as JPEG files,
                so there's no need to keep original file extension.
                For example::
                    import os.path as op
                    def thumb_name(filename):
                        name, _ = op.splitext(filename)
                        return secure_filename('%s-thumb.jpg' % name)
                    class MyForm(BaseForm):
                        upload = ImageUploadField('File', thumbgen=thumb_name)
            :param thumbnail_size:
                Tuple or (width, height, force) values. If not provided, thumbnail won't be created.
                Width and height is in pixels. If `force` is set to `True`, will try to fit image into dimensions and
                keep aspect ratio, otherwise will just resize to target size.
            :param url_relative_path:
                Relative path from the root of the static directory URL. Only gets used when generating
                preview image URLs.
                For example, your model might store just file names (`relative_path` set to `None`), but
                `base_path` is pointing to subdirectory.
            :param endpoint:
                Static endpoint for images. Used by widget to display previews. Defaults to 'static'.
        """

        if not label:
            label = 'File'

        if not base_path:
            base_path = current_app.config['MEDIA_ROOT']

        if not relative_path:
            relative_path = 'images/'

        if not namegen:
            namegen = namegen_filename

        if not allowed_extensions:
            allowed_extensions = current_app.config[
                'IMAGES_ALLOWED_EXTENSIONS']

        thumbgen = thumbgen_filename
        thumbnail_size = (100, 100, False)

        if not endpoint:
            endpoint = 'main.download_file_by_filename'

        super(DropImageUploadField, self).__init__(
            label, validators,
            base_path=base_path,
            relative_path=relative_path,
            namegen=namegen,
            allowed_extensions=allowed_extensions,
            thumbgen=thumbgen,
            thumbnail_size=thumbnail_size,
            permission=permission,
            endpoint=endpoint,
            **kwargs)


class MultipleImageUploadInput(object):

    """
        Render a image input chooser field which you can choose multiple images.
        You can customize `empty_template` and `data_template` members to customize
        look and feel.
    """

    empty_template = ('<input %(file)s multiple>')

    data_template = ('<input %(file)s multiple><br/>'
                     '<div class="card-columns">'
                     '    %(images)s'
                     '</div>')

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        kwargs.setdefault('name', field.name)

        args = {"file": html_params(type="file", **kwargs)}

        if field.data and isinstance(field.data, string_types):

            attributes = self.get_attributes(field)

            args["images"] = "&emsp;".join(
                [('<div class="card">'
                  '<img src="{src}" class="card-img-top"/>'
                  '<div class="card-body">'
                  '<div class="form-check">'
                  '<input class="form-check-input" type="checkbox" name="_{filename}-delete" id="_{filename}-delete"/>'
                  '<label class="form-check-label" for="_{filename}-delete">{text}</label>'
                  '</div>'
                  '</div>'
                  '</div>').format(src=src, filename=filename, text=__('Eliminar')) for src, filename in attributes])

            template = self.data_template

        else:
            template = self.empty_template

        return HTMLString(template % args)

    def get_attributes(self, field):

        for item in ast.literal_eval(field.data):

            filename = item

            if field.thumbnail_size:
                filename = field.thumbnail_fn(filename)

            if field.url_relative_path:
                filename = urljoin(field.url_relative_path, filename)

            yield get_url(field.endpoint, filename=filename), item


class MultipleImageUploadField(ImageUploadField):
    """
        Multiple image upload field.
        Does image validation, thumbnail generation, updating and deleting images.
        Requires PIL (or Pillow) to be installed.
    """

    widget = MultipleImageUploadInput()

    def __init__(self, label=None, validators=None,
                 base_path=None, relative_path=None,
                 namegen=None, allowed_extensions=None,
                 max_size=None,
                 thumbgen=None, thumbnail_size=None,
                 permission=0o666,
                 url_relative_path=None, endpoint=None,
                 **kwargs):
        """
            Constructor.
            :param label:
                Display label
            :param validators:
                Validators
            :param base_path:
                Absolute path to the directory which will store files
            :param relative_path:
                Relative path from the directory. Will be prepended to the file name for uploaded files.
                Flask-Admin uses `urlparse.urljoin` to generate resulting filename, so make sure you have
                trailing slash.
            :param namegen:
                Function that will generate filename from the model and uploaded file object.
                Please note, that model is "dirty" model object, before it was committed to database.
                For example::
                    import os.path as op
                    def prefix_name(obj, file_data):
                        parts = op.splitext(file_data.filename)
                        return secure_filename('file-%s%s' % parts)
                    class MyForm(BaseForm):
                        upload = FileUploadField('File', namegen=prefix_name)
            :param allowed_extensions:
                List of allowed extensions. If not provided, then gif, jpg, jpeg, png and tiff will be allowed.
            :param max_size:
                Tuple of (width, height, force) or None. If provided, Flask-Admin will
                resize image to the desired size.
                Width and height is in pixels. If `force` is set to `True`, will try to fit image into dimensions and
                keep aspect ratio, otherwise will just resize to target size.
            :param thumbgen:
                Thumbnail filename generation function. All thumbnails will be saved as JPEG files,
                so there's no need to keep original file extension.
                For example::
                    import os.path as op
                    def thumb_name(filename):
                        name, _ = op.splitext(filename)
                        return secure_filename('%s-thumb.jpg' % name)
                    class MyForm(BaseForm):
                        upload = ImageUploadField('File', thumbgen=thumb_name)
            :param thumbnail_size:
                Tuple or (width, height, force) values. If not provided, thumbnail won't be created.
                Width and height is in pixels. If `force` is set to `True`, will try to fit image into dimensions and
                keep aspect ratio, otherwise will just resize to target size.
            :param url_relative_path:
                Relative path from the root of the static directory URL. Only gets used when generating
                preview image URLs.
                For example, your model might store just file names (`relative_path` set to `None`), but
                `base_path` is pointing to subdirectory.
            :param endpoint:
                Static endpoint for images. Used by widget to display previews. Defaults to 'static'.
        """

        if not label:
            label = 'File'

        if not base_path:
            base_path = current_app.config['MEDIA_ROOT']

        if not relative_path:
            relative_path = 'images/'

        if not namegen:
            namegen = namegen_filename

        if not allowed_extensions:
            allowed_extensions = current_app.config[
                'IMAGES_ALLOWED_EXTENSIONS']

        thumbgen = thumbgen_filename

        if not endpoint:
            endpoint = 'main.download_file_by_filename'

        super(MultipleImageUploadField, self).__init__(
            label, validators,
            base_path=base_path,
            relative_path=relative_path,
            namegen=namegen,
            allowed_extensions=allowed_extensions,
            thumbgen=thumbgen,
            thumbnail_size=thumbnail_size,
            permission=permission,
            endpoint=endpoint,
            **kwargs)

    def process(self, formdata, data=unset_value):
        self.formdata = formdata

        return super(MultipleImageUploadField, self).process(formdata, data)

    def process_formdata(self, valuelist):
        self.data = list()

        for value in valuelist:
            if self._is_uploaded_file(value):
                self.data.append(value)

    def populate_obj(self, obj, name):
        field = getattr(obj, name, None)

        if field:
            filenames = ast.literal_eval(field)

            for filename in filenames[:]:

                if "_{}-delete".format(filename) in self.formdata:
                    self._delete_file(filename)
                    filenames.remove(filename)

        else:

            filenames = list()

        for data in self.data:

            if self._is_uploaded_file(data):

                try:
                    self.image = Image.open(data)
                except Exception as e:
                    raise ValidationError('Invalid image: %s' % e)

                filename = self.generate_name(obj, data)
                filename = self._save_file(data, filename)
                data.filename = filename

                filenames.append(filename)

        setattr(obj, name, str(filenames))


class ImageUploadFieldApp(ImageUploadField):

    widget = ImageUploadInput()

    widget.data_template = ('<input %(file)s><br>'
                     '<div class="card-columns">'
                     '<div class="card">'
                     ' <img %(image)s>'
                     '<div class="card-body">'
                        '<div class="form-check">'
                            '<input class="form-check-input" type="checkbox" name="%(marker)s">'
                            '<label class="form-check-label">Eliminar</label></input>'
                        '</div>'
                    '</div>'
                     ' <input %(text)s>'
                     '</div></div>')

    def __init__(self, label=None, validators=None,
                 base_path=None, relative_path=None,
                 namegen=None, allowed_extensions=None,
                 max_size=None,
                 thumbgen=None, thumbnail_size=None,
                 permission=0o666,
                 url_relative_path=None, endpoint=None,
                 **kwargs):

        if not label:
            label = 'File'

        if not base_path:
            base_path = current_app.config['MEDIA_ROOT']

        if not relative_path:
            relative_path = 'images/'

        if not namegen:
            namegen = namegen_filename

        if not allowed_extensions:
            allowed_extensions = current_app.config[
                'IMAGES_ALLOWED_EXTENSIONS']

        thumbgen = thumbgen_filename

        if not endpoint:
            endpoint = 'main.download_file_by_filename'

        if Image is None:
            raise ImportError('PIL library was not found')

        self.max_size = max_size
        self.thumbnail_fn = thumbgen or thumbgen_filename
        self.thumbnail_size = thumbnail_size
        self.endpoint = endpoint
        self.image = None
        self.url_relative_path = url_relative_path

        if not allowed_extensions:
            allowed_extensions = ('gif', 'jpg', 'jpeg', 'png', 'tiff')

        super(ImageUploadField, self).__init__(label, validators,
                                               base_path=base_path,
                                               relative_path=relative_path,
                                               namegen=namegen,
                                               allowed_extensions=allowed_extensions,
                                               permission=permission,
                                               **kwargs)


class ImageUploadFieldAppLogo(ImageUploadFieldApp):
    def __init__(self, label=None, validators=None,
                 base_path=None, relative_path=None,
                 namegen=None, allowed_extensions=None,
                 max_size=None,
                 thumbgen=None, thumbnail_size=None,
                 permission=0o666,
                 url_relative_path=None, endpoint=None,
                 **kwargs):
        super(ImageUploadFieldAppLogo, self).__init__(label='Logo', validators=None,
                 base_path=None, relative_path=None,
                 namegen=None, allowed_extensions=None,
                 max_size=None,
                 thumbgen=None, thumbnail_size=None,
                 permission=0o666,
                 url_relative_path=None, endpoint=None,
                 **kwargs)


class MultipleImageUploadFieldPortada(MultipleImageUploadField):
    def __init__(self, label=None, validators=None,
                 base_path=None, relative_path=None,
                 namegen=None, allowed_extensions=None,
                 max_size=None,
                 thumbgen=None, thumbnail_size=None,
                 permission=0o666,
                 url_relative_path=None, endpoint=None,
                 **kwargs):
        super(MultipleImageUploadFieldPortada, self).__init__(label='Portada', validators=None,
                     base_path=None, relative_path=None,
                     namegen=None, allowed_extensions=None,
                     max_size=None,
                     thumbgen=None, thumbnail_size=None,
                     permission=0o666,
                     url_relative_path=None, endpoint=None,
                     **kwargs)