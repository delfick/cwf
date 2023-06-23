from django.urls import reverse

class AdminView(object):
    """Stateless Object that knows how to get url to an admin view"""
    @classmethod
    def format(cls, content_type, page):
        return "admin:%s_%s_%s" % (content_type.app_label, content_type.model, page)

    @classmethod
    def change_view(cls, obj):
        """Admin change view for a particular instance of an object"""
        from django.contrib.contenttypes.models import ContentType
        content_type = ContentType.objects.get_for_model(obj.__class__)
        format = cls.format(content_type, "change")
        return reverse(format, args=(obj.id, ))

    @classmethod
    def add_view(cls, obj):
        """Admin add view for a particular model"""
        from django.contrib.contenttypes.models import ContentType
        content_type = ContentType.objects.get_for_model(obj)
        format = cls.format(content_type, "add")
        return reverse(format)

    @classmethod
    def change_list(cls, obj):
        """Admin list view for a particular model"""
        from django.contrib.contenttypes.models import ContentType
        content_type = ContentType.objects.get_for_model(obj)
        format = cls.format(content_type, "changelist")
        return reverse(format)
