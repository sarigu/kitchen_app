from django.db import models

# Create your models here.

def user_directory_path(instance, filename):
    return 'images/{0}/'.format(filename)

class Images(models.Model):
    title = models.CharField(max_length=250)
    alt = models.TextField(null=True)
    image = models.ImageField(upload_to=user_directory_path, default='posts/default.jpg')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.alt}  - {self.created_at}"