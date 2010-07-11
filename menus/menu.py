class Menu(object):
    def __init__(self, site, selectedSection, remainingUrl):
        self.site = site
        self.remainingUrl = remainingUrl
        self.selectedSection = selectedSection
    
    def getGlobal(self):
        for section in self.site:
            if section == self.selectedSection:
                section.selected = True
            else:
                section.selected = False
            yield section.getInfo(self.remainingUrl)
        
    def heirarchial(self, section=None, path=None, parentUrl=None, parentSelected=False):
        if not section:
            section = self.selectedSection
            
        if not path:
            path = [p for p in self.remainingUrl]
        
        if parentUrl is None:
            parentUrl = []
            
        if section.options.showBase:
            for info in section.getInfo(path, parentUrl, parentSelected, self.heirarchial):
                yield info
            
        else:
            if section.url:
                parentUrl.append(section.url)
                
            for child in section.children:
                yield child.getInfo(path, parentUrl, parentSelected, self.hierarchial)
                
    def layered(self, selected=None, path=None, parentUrl = None, parentSelected=False):
        if not selected:
            selected = self.selectedSection
        
        if not path:
            path = [p for p in self.remainingUrl]
            
        if parentUrl is None:
            parentUrl = []
            
        while selected:
            l = []
            anySelected = False
            for part in self.getLayer(selected, path, parentUrl, parentSelected):
                l.append(part)
                _, _, _, isSelected, _, _ = part
                if isSelected:
                    selected = part
                    anySelected = True
            
            if not anySelected:
                selected = None
        
        yield l
    
    def getLayer(self, section, path, parentUrl, parentselected):
        if section.options.showBase:
            yield section.getInfo(path, parenturl, parentSelected, self.layered)
        
        else:
            if section.url:
                parentUrl.append(section.url)
                
            l = [child.getLayer(child, path) for child in section.children]
            for part in chain.from_iterable(l):
                yield part.getInfo(path, parentUrl, parentSelected, self.layered)
    
