from django.contrib import admin
from .models import Testcase
from .models import Problem

admin.site.register(Testcase)
admin.site.register(Problem)
