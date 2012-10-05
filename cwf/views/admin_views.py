from django.contrib.contenttypes.models import ContentType
from django.core import urlresolvers

class AdminView(object):
    """Object that knows how to get url to an admin view for an object"""
    @classmethod
    def format(cls, content_type, page):
        return "admin:%s_%s_%s" % (content_type.app_label, content_type.model, page)

    @classmethod
    def change_view(cls, obj):
        content_type = ContentType.objects.get_for_model(obj.__class__)
        format = cls.format(content_type, "change")
        return urlresolvers.reverse(format, args=(obj.id, ))

    @classmethod
    def add_view(cls, obj):
        content_type = ContentType.objects.get_for_model(obj)
        format = cls.format(content_type, "add")
        return urlresolvers.reverse(format)

    @classmethod
    def change_list(cls, obj):
        content_type = ContentType.objects.get_for_model(obj)
        format = cls.format(content_type, "changelist")
        return urlresolvers.reverse(format)
