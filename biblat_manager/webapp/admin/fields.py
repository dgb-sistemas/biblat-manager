import operator
from collections import OrderedDict

from flask import url_for
from wtforms.fields import SelectField, StringField, HiddenField, Field, Label
from wtforms.widgets import HTMLString, html_params, TextInput, HiddenInput
from wtforms.widgets import Select
from flask_admin.contrib.sqla.fields import QuerySelectField
from flask_admin.form.fields import Select2Field
from flask_admin._compat import string_types, text_type
from markupsafe import Markup, escape


# GroupSelect based on https://gist.github.com/playpauseandstop/1590178

__all__ = (
    'GroupSelectField',
    'GroupSelectWidget',
    'GroupSelect2Widget',
    'QueryGroupSelectField',
    'MapSearchWidget',
    'MapSearchField',
    'HiddenDetailSearchField',
    'HiddenDetailSearchWidget',
    'AppendSelect2Field')


class GroupSelectWidget(Select):
    """
    Add support of choices with ``optgroup`` to the ``Select`` widget.
    """

    def __call__(self, field, **kwargs):
        kwargs.setdefault("id", field.id)
        if self.multiple:
            kwargs["multiple"] = True
        if "required" not in kwargs and "required" in getattr(field, "flags", []):
            kwargs["required"] = True
        html = ["<select %s>" % html_params(name=field.name, **kwargs)]
        for val, label, selected in field.iter_choices():
            if isinstance(val, (list, tuple)):
                html.append('<optgroup %s>' % html_params(label=label))
                for inner_val, inner_label, selected_inner in val:
                    html.append(self.render_option(inner_val, inner_label, selected_inner))
                html.append('</optgroup>')
            else:
                html.append(self.render_option(val, label, selected))
        html.append("</select>")
        return HTMLString("".join(html))


class GroupSelectField(SelectField):
    """
    Add support of ``optgroup`` grouping to default WTForms' ``SelectField`` class.
    Here is an example of how the data is laid out.
        (
            ('Fruits', (
                ('apple', 'Apple'),
                ('peach', 'Peach'),
                ('pear', 'Pear')
            )),
            ('Vegetables', (
                ('cucumber', 'Cucumber'),
                ('potato', 'Potato'),
                ('tomato', 'Tomato'),
            )),
            ('other','None Of The Above')
        )
    It's a little strange that the tuples are (value, label) except for groups which are (Group Label, list of tuples)
    but this is actually how Django does it too https://docs.djangoproject.com/en/dev/ref/models/fields/#choices
    """
    widget = GroupSelectWidget()

    def pre_validate(self, form):
        """
        Don't forget to validate also values from embedded lists.
        """
        for item1, item2 in self.choices:
            if isinstance(item2, (list, tuple)):
                group_label = item1
                group_items = item2
                for val,label in group_items:
                    if val == self.data:
                        return
            else:
                val = item1
                label = item2
                if val == self.data:
                    return
        raise ValueError(self.gettext('Not a valid choice!'))


class GroupSelect2Widget(GroupSelectWidget):
    """
        `Select2 <https://github.com/ivaynberg/select2>`_ styled select widget.
        You must include select2.js, form-x.x.x.js and select2 stylesheet for it to
        work.
    """

    def __call__(self, field, **kwargs):
        kwargs.setdefault('data-role', u'select2')

        allow_blank = getattr(field, 'allow_blank', False)
        if allow_blank and not self.multiple:
            kwargs['data-allow-blank'] = u'1'

        return super(GroupSelect2Widget, self).__call__(field, **kwargs)


class QueryGroupSelectField(QuerySelectField):
    widget = GroupSelect2Widget()

    def __init__(self, label=None, validators=None, query_factory=None,
                 get_pk=None, get_label=None, get_label_group=None,
                 allow_blank=False, blank_text=u'', **kwargs):
        super(QueryGroupSelectField, self).__init__(label=label,
                                                    validators=validators,
                                                    query_factory=query_factory,
                                                    get_pk=get_pk,
                                                    get_label=get_label,
                                                    allow_blank=allow_blank,
                                                    blank_text=blank_text,
                                                    **kwargs)
        if get_label_group is None:
            self.get_label_group = lambda x: x
        elif isinstance(get_label_group, string_types):
            self.get_label_group = operator.attrgetter(get_label_group)
        else:
            self.get_label_group = get_label_group

    def iter_choices(self):
        if self.allow_blank:
            yield (u'__None', self.blank_text, self.data is None)
        group_list = OrderedDict()
        for pk, obj in self._get_object_list():
            try:
                group_list.setdefault(self.get_label_group(obj), []).append((pk, self.get_label(obj), obj == self.data))
            except:
                group_list.update({pk: obj})

        for label_group, group in group_list.items():
            if isinstance(group, (list, tuple)):
                yield (group, label_group, False)
            else:
                yield (label_group, self.get_label(group), group == self.data)


class MapSearchWidget(TextInput):
    def __call__(self, field, **kwargs):
        kwargs.setdefault("id", field.id)
        kwargs.setdefault("type", self.input_type)
        kwargs.setdefault("class", "geocomplete")
        kwargs['autocomplete'] = 'off'
        kwargs['class'] += ' geocomplete'
        if "value" not in kwargs:
            kwargs["value"] = field._value()
        if "required" not in kwargs and "required" in getattr(field, "flags",
                                                              []):
            kwargs["required"] = True
        html = ['<div class="input-group">',
                '<input %s>' % self.html_params(name=field.name, **kwargs),
                '<div class="input-group-append">',
                '<button class="btn btn-outline-secondary" id="find" type="button"><i class="fas fa-search-location"></i></button>',
                '</div>',
                '</div></div><div class="col-md-10"><div class="map_canvas">']
        return HTMLString("".join(html))


class MapSearchField(StringField):
    widget = MapSearchWidget()


class HiddenDetailSearchWidget(HiddenInput):
    def __call__(self, field, **kwargs):
        kwargs.setdefault("id", field.id)
        kwargs.setdefault("type", self.input_type)
        if "value" not in kwargs:
            kwargs["value"] = field._value()
        if "required" not in kwargs and "required" in getattr(field, "flags",
                                                              []):
            kwargs["required"] = True
        html = ['<div class="details">',
                '<input %s>' % self.html_params(name=field.name, **kwargs),
                '</div>']
        return HTMLString("".join(html))


class HiddenDetailSearchField(HiddenField):
    widget = HiddenDetailSearchWidget()


class AppendSelectWidget(Select):
    def __call__(self, field, **kwargs):
        kwargs.setdefault("id", field.id)
        append_text = getattr(field, 'append_text', 'Add')
        modal_title = getattr(field, 'modal_title', 'Crear New Record')
        if self.multiple:
            kwargs["multiple"] = True
        if "required" not in kwargs and "required" in getattr(field, "flags",
                                                              []):
            kwargs["required"] = True
        html = ['<div class="input-group">',
                "<select %s>" % html_params(name=field.name, **kwargs)]
        for val, label, selected in field.iter_choices():
            html.append(self.render_option(val, label, selected))
        html.append("</select>")
        html.append('<div class="input-group-append"><button class="btn btn-outline-secondary btn-sm append-select" id="append_%s" type="button" data-target="#fa_modal_window" data-remote="%s" data-toggle="modal">' % (field.id.replace('_id', ''), url_for('%s.create_view' % field.id.replace('_id', ''), modal=True)))
        html.append('<i class="fas fa-plus-circle"></i> %s' % append_text)
        html.append('</button></div>')
        html.append("</div>")
        return HTMLString("".join(html))


class AppendSelectField(SelectField):
    widget = AppendSelectWidget()


class AppendSelect2Widget(AppendSelectWidget):
    def __call__(self, field, **kwargs):
        kwargs.setdefault('data-role', u'select2')

        allow_blank = getattr(field, 'allow_blank', False)
        if allow_blank and not self.multiple:
            kwargs['data-allow-blank'] = u'1'

        return super(AppendSelect2Widget, self).__call__(field, **kwargs)


class AppendSelect2Field(Select2Field):
    widget = AppendSelect2Widget()

    def __init__(self, label=None, validators=None, coerce=text_type,
                 choices=None, allow_blank=False, blank_text=None, append_text=None, modal_title=None, **kwargs):
        self.append_text = append_text or 'Add'
        self.modal_title = modal_title
        super(AppendSelect2Field, self).__init__(
            label=label, validators=validators, coerce=coerce,
            choices=choices, allow_blank=allow_blank, blank_text=blank_text, **kwargs
        )


class AppendFieldWidget(object):
    def __call__(self, field, **kwargs):
        html = ['<button type="button" class="btn btn-secondary add-event" id="append_%s" type="button" data-target="#fa_modal_window" data-remote="%s" data-toggle="modal">Agregar</button>' % (
            field.id.replace('_id', ''),
            url_for('%s.create_view' % field.id.replace('_id', ''),
                    modal=True))]
        return HTMLString("".join(html))


class LabelAppend(Label):
    def __call__(self, text=None, **kwargs):
        if "for_" in kwargs:
            kwargs["for"] = kwargs.pop("for_")
        else:
            kwargs.setdefault("for", self.field_id)

        attributes = widgets.html_params(**kwargs)
        text = escape(text or self.text)
        return Markup("<label %s>%s</label>" % (attributes, text))


class AppendField(Field):
    widget = AppendFieldWidget()

