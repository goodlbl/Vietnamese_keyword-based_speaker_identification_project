from django.db import models

class ButtonState(models.Model):
    index = models.IntegerField(unique=True)   # nút thứ mấy (1-6)
    state = models.BooleanField(default=False) # True = 1, False = 0

    def __str__(self):
        return f"Button {self.index}: {int(self.state)}"
