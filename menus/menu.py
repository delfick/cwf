from itertools import chain

class Menu(object):
    """Wrapper around sections and sites for getting necessary menu information"""
    
    def __init__(self, site, remainingUrl, selectedSection=None):
        self.site = site
        self.remainingUrl = remainingUrl
        self.selectedSection = selectedSection
    
    def getGlobal(self):
        """Get sections in the site's menu"""
        for section in self.site.menu():
            for info in section.getInfo(self.remainingUrl):
                yield info
        
    def heirarchial(self, sections=None, path=None, parentUrl=None, parentSelected=True):
        """Get menu for selected section as a heirarchy"""
        if not sections:
            sections = []
            if self.selectedSection:
                sections = [self.selectedSection]
        
        for section in sections:
            
            if path is None:
                path = [p for p in self.remainingUrl]
            
            if parentUrl is None:
                parentUrl = []
                
            if section.options.showBase:
                for info in section.getInfo(path, parentUrl, parentSelected, self.heirarchial):
                    yield info
                
            else:
                if section.url:
                    parentUrl.append(section.url)
                selected, path = section.determineSelection(path, parentSelected)
                parentSelected = parentSelected and selected
                
                for child in section.children:
                    for info in child.getInfo(path, parentUrl, parentSelected, self.heirarchial):
                        yield info
                
    def layered(self, selected=None, path=None, parentUrl = None, parentSelected=True):
        """Get menu for selected section per layer"""
        if not selected:
            selected = self.selectedSection
        
        if path is None:
            path = [p for p in self.remainingUrl]
            
        if parentUrl is None:
            parentUrl = []
            
        while selected:
            # Whilst we still have a selected section (possibility of more layers)
            l = []
            anySelected = False
            for part in self.getLayer(selected, path, parentUrl, parentSelected):
                l.append(part)
                _, _, _, isSelected, _, _ = part
                if isSelected:
                    selected = part[0]
                    anySelected = True
            
            if not anySelected:
                selected = None
        
        yield l
    
    def getLayer(self, section, path, parentUrl, parentSelected):
        """Function to get next layer for a section"""
        if section.options.showBase:
            for info in section.getInfo(path, parentUrl, parentSelected):
                yield info
        else:
            if section.url:
                parentUrl.append(section.url)
                
            selected, path = section.determineSelection(path, parentSelected)
            parentSelected = parentSelected and selected
                
            l = [self.getLayer(child, path, parentUrl, parentSelected) for child in section.children]
            for info in chain.from_iterable(l):
                yield info
    
