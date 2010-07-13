from django.db import models
        
class Part1Model(models.Model):
    text = models.CharField()
    
    class Meta:
        app_label = 'example'

__all__ = [Part1Model]
