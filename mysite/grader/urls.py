from django.urls import path, register_converter
from django.conf import settings
from django.conf.urls.static import static

from . import views

app_name = 'grader'
urlpatterns = [
    path('submissions', views.submission_list, name='submission_list'),
    path('', views.problem_list, name='problem_list'),
    path('upload', views.upload_problem, name='upload_problem'),
    
    path('problems/<pid>', views.testcase_list, name='testcase_list'),
    path('problems/<pid>/testcase/upload', views.upload_testcase, name='upload_testcase'),
    path('problems/<pid>/testcase/<int:pk>', views.delete_testcase, name='delete_testcase'),
    
    # path('testcase/<uuid:pid>', views.delete_testcase, name='delete_testcase'),
    # path('up', views.upload_file, name='upload_file'),
] 
