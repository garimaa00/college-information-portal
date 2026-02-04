from django.db import models

class Course(models.Model):
    name = models.CharField(max_length=100)  # e.g., BBA, BIM
    level = models.CharField(max_length=10, choices=[('bachelor', 'Bachelor'), ('master', 'Master')])
    seats = models.IntegerField(default=0)
    fee_structure = models.TextField()  # e.g., "Annual: $5000"

    def __str__(self):
        return self.name

class Testimonial(models.Model):
    name = models.CharField(max_length=100)
    content = models.TextField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} - {self.course.name}"