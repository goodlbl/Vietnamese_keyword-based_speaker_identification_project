from django.db import models
import json

class MemberRecord(models.Model):
    name = models.CharField(max_length=100)
    buttons = models.JSONField()  # lưu [0,1,1,0,0,1]
    audio1 = models.FileField(upload_to='audios/', null=True, blank=True)
    audio2 = models.FileField(upload_to='audios/', null=True, blank=True)
    audio3 = models.FileField(upload_to='audios/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.created_at:%Y-%m-%d %H:%M:%S})"
