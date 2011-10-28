import rendering

########################
###   BACKUP BUTTON FUNCTIONS
########################

def backupHelper(action, message):
    def helper(request, obj, button):
        if request.GET and request.GET.get("yes"):
            getattr(obj, action)()
            url = '/admin/%s/%s/%s' % (obj._meta.app_label, obj._meta.module_name, obj.id)
            return rendering.redirect(url)
        else:
            return 'other/decision.html', {'message' : message}
    return helper

class SingularBackupRestoreMixin(object):
    """Action for basic backup and restore functions
    Use with:
        buttons = (
            Button('backup', "Backup"),
            Button('restore', "Restore", saveOnClick=False),
        )
    """
    def tool_backupRestore_helper(self, *args, **kwargs):
        return backupHelper("create", "Are you sure you want to make a backup?")(*args, **kwargs)
    
    def tool_restore(self, *args, **kwargs):
        return backupHelper(
                "restoreBackup", "Are you sure you want to restore from the backup?"
            )(*args, **kwargs)

########################
###   BACKUP ACTION FUNCTIONS
########################
        
class ActionBackupRestoreMixin(object):
    """Mixin for basic backup and restore actions
    Use with :
        actions = ['backup', 'restore']
    """

    def backup(self, request, queryset):
        xml = queryset.model().infoXml()
        xml.generate(queryset.model.objects, xml=xml)
    backup.short_description = "Backup all of them"

    def restore(self, request, queryset):
        xml = queryset.model().infoXml()
        xml.restore(queryset.model, {}, xml=xml)
    restore.short_description = "Restore all of them"
