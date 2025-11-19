from django.db import models
from django.core.validators import RegexValidator
from django.core.validators import MaxLengthValidator

class Room(models.Model):
    room_number = models.CharField(
        max_length=10,
        unique=True,
        validators=[
            MaxLengthValidator(10, message='Room name không được quá 10 ký tự.')
    ]
    )
    password = models.CharField(max_length=50)
    owner = models.ForeignKey('member_registering_page.MemberRecord', on_delete=models.CASCADE, related_name='owned_rooms')
    total_members = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Phòng {self.room_number} (Chủ: {self.owner})"
    
    class Meta:
        db_table = 'room'
        verbose_name = 'Room'
        verbose_name_plural = 'Rooms'
