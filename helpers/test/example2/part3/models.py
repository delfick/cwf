from django.db import models
        
class Part3Model(models.Model):
    blah = models.IntegerField(default=0)
    
    class Meta:
        app_label = 'example2'

__all__ = [Part3Model]
