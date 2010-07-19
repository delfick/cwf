from itertools import chain

class Menu(object):
    """Wrapper around sections and sites for getting necessary menu information"""
    
    def __init__(self, site, remainingUrl, selectedSection=None, request=None):
        self.site    = site
        self.request = request
        
        self.remainingUrl    = remainingUrl
        self.selectedSection = selectedSection
    
    def clean(self, info):
        section, fullUrl, alias, selected, children, options = info
        if fullUrl == ['']:
            fullUrl = ['', '']
        
        elif fullUrl and fullUrl[-1] == '':
            fullUrl = fullUrl[:-1]
        
        return (section, fullUrl, alias, selected, children, options)
    
    def getGlobal(self):
        """Get sections in the site's menu"""
        
        path = [p.lower() for p in self.remainingUrl]
        
        for section in self.site.menu():
            parentUrl, remaining, inside = self.site.getPath(section, path[:])
            
            parentSelected = False
            if inside:
                if path == [] and not parentUrl:
                    parentSelected = True

                else:
                    if not parentUrl and section.url and remaining:
                        if remaining[0] == str(section.url).lower():
                            parentSelected = True

                    elif path == parentUrl:
                        parentSelected = True

                    else:
                        zipped = zip(parentUrl, path)
                        if zipped:
                            parentSelected = len(parentUrl) > 0 and all(d == e for (d, e) in zipped)

            for info in section.getInfo(remaining, parentUrl, parentSelected, request=self.request):
                yield self.clean(info)
        
    def heirarchial(self, includeFirst=False):
        """Get menu for selected section as a heirarchy"""
        if self.selectedSection:
            path = [p for p in self.remainingUrl]
            parentUrl, path, _ = self.site.getPath(self.selectedSection.rootAncestor(), path)
            parentSelected = True
            
            if not includeFirst:
                section = self.selectedSection
                if section.url:
                    parentUrl.append(section.url)
                    selected, path = section.determineSelection(path, parentSelected)
                    parentSelected = parentSelected and selected
                    
                sections = section.children
            else:
                sections = []
                if self.selectedSection:
                    sections = [self.selectedSection]
                
            for info in self.getHeirarchy(sections, path, parentUrl, parentSelected, request=self.request):
                yield self.clean(info)
        
    def getHeirarchy(self, sections, path, parentUrl, parentSelected, request=None):
        """Generator function for heirarchial menu children"""
        for section in sections:
            if section.options.showBase:
                for info in section.getInfo(path, parentUrl, parentSelected, self.getHeirarchy, request=request):
                    yield info
                
            else:
                if section.url:
                    parentUrl.append(section.url)
                    
                selected, path = section.determineSelection(path, parentSelected)
                parentSelected = parentSelected and selected
                
                for child in section.children:
                    for info in child.getInfo(path, parentUrl, parentSelected, self.getHeirarchy, request=request):
                        yield info
        
                    
    def layered(self, includeFirst=False):
        """Get menu for selected section per layer"""
        if self.selectedSection:
            path      = [p for p in self.remainingUrl]
            parentUrl = []
            parentSelected = True
            
            if not includeFirst:
                parentUrl, path, _ = self.site.getPath(self.selectedSection.rootAncestor(), path)
                section = self.selectedSection
                if section.url:
                    parentUrl.append(section.url)
                    selected, path = section.determineSelection(path, parentSelected)
                    parentSelected = parentSelected and selected
                
                selected = self.getLayer(section.children, path, parentUrl, parentSelected, request=self.request)
            else:
                selected  = self.getLayer([self.selectedSection], path, parentUrl, parentSelected, request=self.request)
            
            while selected:
                # Whilst we still have a selected section (possibility of more layers)
                l = []
                anySelected  = False
                for part in selected:
                    section, _, _, isSelected, children, _ = part
                    if section:
                        l.append(self.clean(part))
                        
                    if isSelected:
                        anySelected  = True
                        selected     = children
                        if callable(children):
                            selected = children()
                
                if not anySelected:
                    selected = None
                
                if l:
                    yield l

    def getLayer(self, sections, path, parentUrl, parentSelected, request=None):
        """Function to get next layer for a section"""
        for section in sections:
            if section.options.showBase:
                for info in section.getInfo(path, parentUrl, parentSelected, self.getLayer, request=request):
                    yield info
            else:
                if section.url:
                    parentUrl.append(section.url)
                    
                selected, path = section.determineSelection(path, parentSelected)
                parentSelected = parentSelected and selected
                    
                for info in self.getLayer(section.children, path, parentUrl, parentSelected):
                    yield info
