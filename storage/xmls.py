from lxml import etree
import os

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
                tree.append(field.section())
        
        return tree
                     
class Xml(object):
    def __init__(self, path=None, default=None, xpath=None):
        self.path = path
        self._tree = None
        self.default = default
        self.xpath = xpath
    
    def getXml(self, everything, count, xml, new=None):
        if xml:
            return xml
        else:
            xml = None
            if any(item for item in everything):
                o = everything[0]
                xml = o.infoXml()
            else:
                if new:
                    next = new(count)
                    xml = next.infoXml()
        
        return xml

    
    def generate(self, query, xml=None, allInOne=True):
        everything = query.all()
        xml = self.getXml(everything, 0, xml)
        if xml:
            if allInOne:
                if len(xml) > len(everything):
                    xml.clear()
            
            for item in everything:
                item.generate()
                
    def restore(self, model, identity, numberedAttr=None, xml=None, finder=None, active=None, zeroBased=False):
        
        def createNew(count):
            next = model(**identity)
            if numberedAttr:
                setattr(next, numberedAttr, count)
            return next
        
        def getDiff(first, second):
            if zeroBased:
                diff = first - second
            else:
                diff = first + 1 - second
            return diff
        
        def startCount():
            count = 1
            if zeroBased:
                count = 0
            return count
                
        query = model.objects.filter(**identity)
        everything = query.all()
        sortedAll = sorted([(getattr(obj, numberedAttr), obj) for obj in everything])
        
        count = startCount()
        
        if finder:
            xml = finder()
        xml = self.getXml(everything, count, xml, createNew)
        
        if active:
            objDiff = len([x for x in xml if active(x)]) - len(everything)
        else:
            objDiff = len(xml) - len(everything)
        
        if objDiff > 0:
            diff = getDiff(objDiff, count)
            for i in range(diff):
                next = createNew(count+i)
                next.save()
        
        query = model.objects.filter(**identity)
        length = max(len(query), len(xml))
        
        countdown = length
        if objDiff < 0:
            countdown = length + objDiff
            
        toDelete = []
        
        def getObjs():
            count = 0
            for item in xml:
                if active and active(item) or not active:
                    yield item, query[count]
                    count += 1
                else:
                    yield item, None
            
            if count < len(query):
                for item in query[count:]:
                    yield None, item
                
        
        count = startCount()
        for section, item in getObjs():
            if item:
                if countdown <= 0 or section is None:
                    toDelete.append(item)
                else:
                    if numberedAttr:
                        setattr(item, numberedAttr, count)
                    item.restore()
                    countdown -= 1
                    
            count += 1
        
        for item in toDelete:
            item.delete()
        
    def indent(self, elem, level=0):
        """Borrowed by http://infix.se/2007/02/06/gentlemen-indent-your-xml"""
        i = "\n" + level*"  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            for e in elem:
                self.indent(e, level+1)
                if not e.tail or not e.tail.strip():
                    e.tail = i + "  "
            if not e.tail or not e.tail.strip():
                e.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i
    
    def clear(self):
        File = open(self.path, 'w')
        File.close()
        
    def save(self):
        File = open(self.path, 'w')
        self.indent(self.tree)
        File.write(etree.tostring(self.tree))
        File.close()
        
    def readFile(self):
        if os.path.exists(self.path):
            try:
                self._tree = etree.parse(open(self.path, 'r')).getroot()
            except:
                self._tree = None
        
        if not self._tree:
            try:
                os.makedirs(os.sep.join(self.path.split(os.sep)[:-1]))
            except OSError:
                pass
                
            self._tree = etree.Element("all")
            self.save()
        
        if self.xpath:
            active = etree.XPath(self.xpath)
            self._tree = active(self._tree)
    
    def __getattr__(self, key):
        if key == 'tree':
            if self._tree is None:
                self.readFile()
            return self._tree
        
        return object.__getattribute__(self, key)
    
    def __len__(self):
        return len(self.tree)
    
    def __iter__(self):
        for item in self.tree:
            yield item
            
    def __getitem__(self, key):
        """Key assumes 1-based instead of 0-based"""
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
                    if self.default:
                        self.tree.append(self.default.section())
                    else:
                        self.tree.append(etree.Element("item"))
                self.save()
                    
            return self.tree[key]
        else:
            raise IndexError("Array access must be done with integers greater than 0")
