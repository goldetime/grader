from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required

from .forms import TestcaseForm
from .forms import ProblemForm
from .models import Testcase
from .models import Problem
from .models import Submission

def submission_list(request):
    p_list = Submission.objects.all()
    paginator = Paginator(p_list, 4) # Show 25 contacts per page
    print(p_list)
    print(type(p_list))

    page = request.GET.get('page')
    try:
        submission = paginator.page(page)
    except PageNotAnInteger:
        submission = paginator.page(1)
    except EmptyPage:
        submission = paginator.page(paginator.num_pages)
    
    return render(request, 'grader/submission.html', {
        'submission': submission
    })

def testcase_list(request, pid):

    testcases_list = Testcase.objects.filter(pid=pid)
    paginator = Paginator(testcases_list, 4) # Show 25 contacts per page

    print(type(paginator))
    print(paginator.page(1))

    page = request.GET.get('page')
    try:
        testcases = paginator.page(page)
    except PageNotAnInteger:
        testcases = paginator.page(1)
    except EmptyPage:
        testcases = paginator.page(paginator.num_pages)
    
    return render(request, 'grader/testcase_list.html', {
        'testcases': testcases,
        'pid': pid
    })

@login_required
def problem_list(request):

    problem_list = Problem.objects.filter(owner_id=request.user)
    paginator = Paginator(problem_list, 4) # Show 25 contacts per page

    page = request.GET.get('page')
    try:
        problems = paginator.page(page)
    except PageNotAnInteger:
        problems = paginator.page(1)
    except EmptyPage:
        problems = paginator.page(paginator.num_pages)
    
    return render(request, 'grader/problem_list.html', {'problems': problems})

def upload_problem(request):
    if request.method == 'POST':
        form = ProblemForm(request.POST)
        if form.is_valid():
            problem = form.save(commit=False)
            problem.owner_id = request.user.id
            problem.save()
            return redirect('grader:problem_list')
    else:
        form = ProblemForm()
    return render(request, 'grader/upload_problem.html', {'form': form})

def upload_testcase(request, pid):
    print(pid)
    if request.method == 'POST':
        # str = TestcaseForm(pid=pid)
        form = TestcaseForm(request.POST, request.FILES)
        if form.is_valid():
            testcase = form.save(commit=False)
            testcase.pid = pid
            testcase.save()
            return redirect('grader:testcase_list', pid)
    else:
        form = TestcaseForm()
    return render(request, 'grader/upload_testcase.html', {
        'form': form,
        'pid': pid,
    })

def delete_testcase(request, pid, pk):
    if request.method == 'POST':
        testcase = Testcase.objects.get(pk=pk)
        testcase.delete()
    return redirect('grader:testcase_list', pid)


# def upload_file(request):
#     context = {}
#     if request.method == 'POST':
#         pid = request.POST.get('pid')
#         u1_file = request.FILES['input']
#         u2_file = request.FILES['output']

#         fs = FileSystemStorage()
        
#         name1 = fs.save(u1_file.name, u1_file)
#         name2 = fs.save(u2_file.name, u2_file)

#         print(name1)
#         print(name2)
#         print(pid)
        
#         # context['url1'] = fs.url(name1)
#         # context['url2'] = fs.url(name2)
        
#     return render(request, 'grader/index.html', context)
