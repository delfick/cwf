from django.db import models
        
class Part2Model(models.Model):
    num = models.IntegerField(default=0)
    
    class Meta:
        app_label = 'example2'

__all__ = [Part2Model]
