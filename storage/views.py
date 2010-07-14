from cwf_new.views import StaffView
from cwf_new.storage import Xml

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
    admin = section.add(name).base(''
        , kls = FinderView
        , display = False
        )
        
    admin.add('find').base(''
        , target = 'find'
        , extraContext = dict(
                model      = model
              , findAfter  = findAfter
              , findBefore = findBefore
              , needsSuperUser = needsSuperUser
          )
        )
        
    admin.add('backup').base(''
        , target = 'backup'
        , extraContext = dict(model=model, needsSuperUser=needsSuperUser)
        )
        
    admin.add('removexml').base(''
        , target = 'removeXml'
        , extraContext = dict(model=model, needsSuperUser=needsSuperUser)
        )
