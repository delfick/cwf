from errors import ConfigurationError

class Values(object):
    '''Holds multiple values for a single section'''
    def __init__(self, values=None, each=None, sorter=None, as_set=True, sort_after_transform=True):
        if not values:
            values = []
        
        # each: Transform each value in values individually into alias, url_part
        #   Must be callable((request, path, parent_url_parts), value)->(alias, url_part)
        self.each = each
        if not callable(self.each):
            raise ConfigurationError("each must be a callable, not %s" % self.each)
        
        # values: The values to use
        #   Can be list or callable((request, path, parent_url_parts))->[]
        self.values = values
        
        # sorter: Function to sort values
        #   If boolean: Determines whether sorting happens at all
        #   If callable: Used as sorted(values, sorter)
        self.sorter = sorter
        if type(sorter) is not bool and not callable(self.sorter):
            raise ConfigurationError("Sorter must be a callable, not %s" % self.sorter)
        
        # as_set: Determine if values should be considered a set to remove duplicates
        #   Sorter will be used after values transformed into a set
        self.as_set = as_set
        
        # sort_after_transform: Determine if sorting happens after self.each is used
        self.sort_after_transform = sort_after_transform
    
    def get_info(self, request, path, parent_url_parts):
        """Yield (alias, url) for each value"""
        # Get sorted values
        info = (request, path, parent_url_parts)
        values = self.get_values(info)
            
        # Yield some information
        if values and any(v is not None for v in values):
            for alias, url in values:
                yield alias, url
    
    def get_values(self, info):
        """Get transformed, sorted values"""
        if not self.values:
            return None
        
        values = normalised_values(info)
        
        # Sort if we have to
        if not self.sort_after_transform:
            values = self.sort(values)
        
        # Tranform as appropiate
        transformed = self.transform_values(values, info)
            
        # Sort if we haven't yet
        if self.sort_after_transform:
            transformed = self.sort(transformed)
        
        return transformed
    
    def transform_values(self, values, info):
        ''''
            use self.each on values if self.each is defined
            self.each will be called as self.each(info, value) for each value in values
            Otherwise turn values list of [v1, v2, v3] into [(v1, v1), (v2, v2), (v3, v3)]
        '''
        if self.each:
            return list(self.each(info, value) for value in values)
        else:
            return [(value, value) for value in values]
    
    def normalised_values(self, info):
        '''
            Return values as a list
            If values is a callable, get the result of calling it with info
            If we want values as set, then do that here
        '''
        # Get a list of values
        values = self.values
        if callable(values):
            values = list(values(info))
        
        # Remove duplicates
        if self.as_set:
            values = set(values)
        
        return values
    
    def sort(self, values):
        """Sort values appropiately"""
        if not self.sorter:
            return values
    
        # Sorting must happen
        if callable(self.sorter):
            return sorted(values, self.sorter)
        else:
            return sorted(values)
