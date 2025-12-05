from django.db import models

class RoomActivity(models.Model):
    STATUS_CHOICES = [
        ('created', 'Created'),   
        ('access', 'Access'),
        ('denied', 'Denied'),    
    ]

    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='access'
    )

    user = models.ForeignKey(
        'member_registering_page.MemberRecord', 
        on_delete=models.CASCADE, 
        related_name='room_activities',
        null=True, blank=True 
    )

    room = models.ForeignKey(
        'room_registering_page.Room', 
        on_delete=models.CASCADE,     
        related_name='activities'     
    )

    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Activity: {self.status}"

    class Meta:
        db_table = 'room_activity'
        ordering = ['-time']