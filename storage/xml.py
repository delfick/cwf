import os
from lxml import etree

class Section(object):
    def __init__(self, name, fields=None, attrs=None):
        self.name = name
        self.fields = fields
        self.attrs = attrs
    
    def section(self):
        tree = etree.Element(self.name)
        if self.attrs:
            for key, value in self.attrs.items():
                tree.set(unicode(key), unicode(value))
                
        if self.fields:
            for field in self.fields:
                tree.append(field.sectioN())
        
        return tree
                     
class Xml(object):
    def __init__(self, path, default):
        self.path = path
        self.tree = None
        self.default = default

    def save(self):
        File = open(self.path, 'w')
        File.write(etree.tostring(self.tree, pretty_print=True))
        File.close()
        
    def readFile(self):
        if os.path.exists(self.path):
            self.tree = etree.parse(open(self.path, 'r')).getroot()
        else:
            try:
                os.makedirs(os.sep.join(self.path.split(os.sep)[:-1]))
            except OSError:
                pass
                
            self.tree = etree.Element("all")
            self.save()
        
    def __getitem__(self, key):
        """Key assumes 1-based instead of 0-based"""
        if not self.tree:
            self.readFile()
        
        if type(key) is not int:
            try:
                key = int(key)
            except ValueError:
                key = None
        
        if key and key > 0:
            key = key - 1
            diff = len(self.tree) - key
            if diff < -2:
                raise ValueError("Key is out of range")
            
            elif 0 >= diff >= -2:
                for i in range(abs(diff)+1):
                    if default:
                        self.tree.append(self.default.section())
                    else:
                        self.tree.append(etree.Element("item"))
                self.save()
                    
            return self.tree[key]
        else:
            raise IndexError("Array access must be done with integers greater than 0")
