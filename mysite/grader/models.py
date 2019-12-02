from django.db import models
from django.contrib.auth.models import User
import uuid

def path(instance, filename):
    return 'problem_{0}/{1}'.format(instance.pid, filename)

class Problem(models.Model):
    pid = models.CharField(max_length=30, unique=True)
    owner = models.ForeignKey(User, related_name='problems', on_delete=models.CASCADE)
    time_limit = models.CharField(max_length=100)
    mem_limit = models.CharField(max_length=100)

class Testcase(models.Model):
    pid = models.CharField(max_length=100)
    tid = models.AutoField(primary_key=True)
    input = models.FileField(upload_to=path, blank=True, null=True)
    output = models.FileField(upload_to=path, blank=True, null=True)
    # problem = models.ForeignKey(Problem, related_name='testcases', on_delete=models.CASCADE)
    
    def __str__(self):
        return str(self.pid)

    def delete(self, *args, **kwargs):
        self.input.delete()
        self.output.delete()
        super().delete(*args, **kwargs)

class Submission(models.Model):
    pid = models.CharField(max_length=100)
    submission_id = models.CharField(max_length=30)
    source = models.FileField(upload_to=path)
    who = models.CharField(max_length=100)
    when = models.DateTimeField('date submited')
    status = models.CharField(max_length=30)

    # problem = models.ForeignKey(Problem, related_name='testcases', on_delete=models.CASCADE)
    # pid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    # pid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # tid = models.AutoField(primary_key=True)
