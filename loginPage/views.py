from django.shortcuts import render
from django.http import HttpResponse

def loginPage(request):
    # return HttpResponse('Hello, World!')
    return render(request,'loginPage/index.html')
# Create your views here.
