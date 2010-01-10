from cwf.views import StaffView
from cwf.storage import Xml

class FinderView(StaffView):
    def can(self, request, needsSuperUser):
        if needsSuperUser and request.user.is_superuser:
            return True
        return False
    
    def find(self, request, model, findBefore=None, findAfter=None, needsSuperUser=True):
        if self.can(request, needsSuperUser):
            xml = Xml()
            
            if findBefore:
                for m in findBefore:
                    xml.find(m)
                    
            xml.find(model)
        
            if findAfter:
                for m in findAfter:
                    xml.find(m)
                
        url = self.getAdminChangeList(model)
        return self.redirect(request, url)
    
    def backup(self, request, model, needsSuperUser=True):
        if self.can(request, needsSuperUser):
            Xml().backup(model)
        url = self.getAdminChangeList(model)
        return self.redirect(request, url)
    
    def removeXml(self, request, model, needsSuperUser=True):
        if self.can(request, needsSuperUser):
            Xml().delete(model)
        url = self.getAdminChangeList(model)
        return self.redirect(request, url)

def addFinderSection(section, name, model, findBefore=None, findAfter=None, needsSuperUser=True):
    admin = section.addSection(name, display=False, obj=FinderView)
    admin.addPage('find', target='find', 
        extraContext=dict(
            model=model, findBefore=findBefore, findAfter=findAfter, needsSuperUser=needsSuperUser
        )
    )
    admin.addPage('backup', target='backup', extraContext=dict(model=model, needsSuperUser=needsSuperUser))
    admin.addPage('removexml', target='removeXml', extraContext=dict(model=model, needsSuperUser=needsSuperUser))
