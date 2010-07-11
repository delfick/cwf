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
                
    def layered(self):
        """Get menu for selected section per layer"""
        path      = [p for p in self.remainingUrl]
        parentUrl = []
        selected  = self.getLayer([self.selectedSection], path, [], True)
        selectedSection = self.selectedSection
            
        while selected:
            # Whilst we still have a selected section (possibility of more layers)
            l = []
            anySelected  = False
            nextSelected = selectedSection
            for part in selected:
                section, _, _, isSelected, children, _ = part
                l.append(part)
                    
                if isSelected:
                    nextSelected = section
                    anySelected  = True
                    selected     = children
                    if callable(children):
                        selected = children()
            
            if not anySelected:
                selected = None
            else:
                selectedSection = nextSelected
            
            if l:
                yield l

    def getLayer(self, sections, path, parentUrl, parentSelected):
        """Function to get next layer for a section"""
        for section in sections:
            if section.options.showBase:
                for info in section.getInfo(path, parentUrl, parentSelected, self.getLayer):
                    yield info
            else:
                if section.url:
                    parentUrl.append(section.url)
                    
                selected, path = section.determineSelection(path, parentSelected)
                parentSelected = parentSelected and selected
                    
                for info in self.getLayer(section.children, path, parentUrl, parentSelected):
                    yield info
