

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Member(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=20, unique=True)
    section = models.CharField(max_length=10)
    is_admin = models.BooleanField(default=False)

   
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} ({self.student_id})"
    
    @property
    def full_name(self):
        return f"{self.user.first_name} {self.user.last_name}"

class Event(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    date = models.DateField(default=timezone.now)
    start_time = models.TimeField()
    end_time = models.TimeField()
    created_by = models.ForeignKey(Member, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title
    
    @property
    def attendance_count(self):
        return self.attendance_set.count()
    
    @property
    def is_ongoing(self):
        now = timezone.now()
        event_date = self.date
        
        if event_date == now.date():
            current_time = now.time()
            return self.start_time <= current_time <= self.end_time
        return False

class Attendance(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['member', 'event']
        
    def __str__(self):
        return f"{self.member} at {self.event}"