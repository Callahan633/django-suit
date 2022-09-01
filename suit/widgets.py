from django import forms, VERSION
from django.contrib.admin.widgets import AdminTimeWidget, AdminDateWidget
from django.forms import Textarea, TextInput, ClearableFileInput
from django.utils.safestring import mark_safe


django_version = VERSION[:2]


class AutosizedTextarea(Textarea):
    """
    AutoSized TextArea - TextArea height dynamically grows based on user input
    """

    def __init__(self, attrs=None):
        new_attrs = _make_attrs(attrs, {"rows": 2}, "autosize form-control")
        super(AutosizedTextarea, self).__init__(new_attrs)

    @property
    def media(self):
        return forms.Media(js=('suit/js/autosize.min.js',))

    def render(self, name, value, attrs=None, renderer=None):
        output = super(AutosizedTextarea, self).render(name, value, attrs)
        output += mark_safe(
            "<script type=\"text/javascript\">django.jQuery(function () { autosize(document.getElementById('id_%s')); });</script>"
            % name)
        return output


class CharacterCountTextarea(AutosizedTextarea):
    """
    TextArea with character count. Supports also twitter specific count.
    """

    def render(self, name, value, attrs=None, renderer=None):
        output = super(CharacterCountTextarea, self).render(name, value, attrs,)
        output += mark_safe(
            "<script type=\"text/javascript\">django.jQuery(function () { django.jQuery('#id_%s').suitCharactersCount(); });</script>"
            % name)
        return output


class ImageWidget(ClearableFileInput):
    def render(self, name, value, attrs=None, renderer=None):
        html = super(ImageWidget, self).render(name, value, attrs,renderer)
        if not value or not hasattr(value, 'url') or not value.url:
            return html
        html = u'<div class="ImageWidget"><div class="float-xs-left">' \
               u'<a href="%s" target="_blank"><img src="%s" width="75"></a></div>' \
               u'%s</div>' % (value.url, value.url, html)
        return mark_safe(html)


class EnclosedInput(TextInput):
    """
    Widget for bootstrap appended/prepended inputs
    """

    def __init__(self, attrs=None, prepend=None, append=None, prepend_class='addon', append_class='addon', onclick_append=None):
        """
        :param prepend_class|append_class: CSS class applied to wrapper element. Values: addon or btn
        """
        self.prepend = prepend
        self.prepend_class = prepend_class
        self.append = append
        self.append_class = append_class
        self.onclick_append = onclick_append
        super(EnclosedInput, self).__init__(attrs=attrs)

    def enclose_value(self, value, wrapper_class):
        if value.startswith("fa-"):
            value = '<i class="fa %s"></i>' % value
        return '<span class="input-group-%s"%s>%s</span>' % (wrapper_class, "onclick="+self.onclick_append if self.onclick_append else "", value)

    def render(self, name, value, attrs=None, renderer=None):
        output = super(EnclosedInput, self).render(name, value, attrs)
        if self.prepend:
            self.prepend = self.enclose_value(self.prepend, self.prepend_class)
            output = '<span class="input-group-text">%s</span>%s' % (self.prepend, output)
        if self.append:
            self.append = self.enclose_value(self.append, self.append_class)
            output = '%s<span class="input-group-text">%s</span>' % (output, self.append, )

        return mark_safe('<div class="input-group">%s</div>' % (output))


class SuitDateWidget(AdminDateWidget):
    def __init__(self, attrs=None, format=None):
        defaults = {'placeholder': _('Date:')[:-1]}
        new_attrs = _make_attrs(attrs, defaults, "vDateField input-small")
        super(SuitDateWidget, self).__init__(attrs=new_attrs, format=format)

    def render(self, name, value, attrs=None, renderer=None):
        if django_version < (1, 11):
            output = super(SuitDateWidget, self).render(name, value, attrs)
        else:
            output = super(SuitDateWidget, self).render(name, value, attrs, renderer)
        return mark_safe(
            '<div class="input-append suit-date">%s<span '
            'class="add-on"><i class="icon-calendar"></i></span></div>' %
            output)


class SuitTimeWidget(AdminTimeWidget):
    def __init__(self, attrs=None, format=None):
        defaults = {'placeholder': _('Time:')[:-1]}
        new_attrs = _make_attrs(attrs, defaults, "vTimeField input-small")
        super(SuitTimeWidget, self).__init__(attrs=new_attrs, format=format)

    def render(self, name, value, attrs=None, renderer=None):
        if django_version < (2, 0):
            output = super(SuitTimeWidget, self).render(name, value, attrs)
        else:
            output = super(SuitTimeWidget, self).render(name, value, attrs, renderer)
        return mark_safe(
            '<div class="input-append suit-date suit-time">%s<span '
            'class="add-on"><i class="icon-time"></i></span></div>' %
            output)


class SuitSplitDateTimeWidget(forms.SplitDateTimeWidget):
    """
    A SplitDateTime Widget that has some admin-specific styling.
    """

    def __init__(self, attrs=None):
        widgets = [SuitDateWidget, SuitTimeWidget]
        forms.MultiWidget.__init__(self, widgets, attrs)

    if django_version < (1, 11):
        def format_output(self, rendered_widgets):
            out_tpl = '<div class="datetime">%s %s</div>'
            return mark_safe(out_tpl % (rendered_widgets[0], rendered_widgets[1]))
    else:
        def render(self, name, value, attrs=None, renderer=None):
            output = super(SuitSplitDateTimeWidget, self).render(name, value, attrs, renderer)
            return mark_safe('<div class="datetime">%s</div>' % output)


def _make_attrs(attrs, defaults=None, classes=None):
    result = defaults.copy() if defaults else {}
    if attrs:
        result.update(attrs)
    if classes:
        result["class"] = " ".join((classes, result.get("class", "")))
    return result
