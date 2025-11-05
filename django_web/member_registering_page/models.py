from django.db import models
import json

class MemberRecord(models.Model):
    name = models.CharField(max_length=100)
    room = models.PositiveIntegerField(null=True, blank=True)
    buttons = models.JSONField(default=list([1,1,1,1,1,1]))
    audio1 = models.BinaryField(null=True, blank=True)
    audio2 = models.BinaryField(null=True, blank=True)
    audio3 = models.BinaryField(null=True, blank=True)
    is_owner = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new and self.room:
            from room_registering_page.models import Room 
            try:
                room = Room.objects.get(id=self.room)
                room.total_members += 1
                room.save()
            except Room.DoesNotExist:
                pass

    def __str__(self):
        return f"{self.name} ({self.created_at:%Y-%m-%d %H:%M:%S})"

    class Meta:
        db_table = 'member_record'
        verbose_name = 'Member Record'
        verbose_name_plural = 'Member Records'
