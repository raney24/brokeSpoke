from django.core.paginator import Paginator
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from .models import *
from .forms import *

# Debugger
import pdb

@login_required(login_url='/')
def timelogs_from_user(request, id):
  usr = Users.objects.get(id=id)
  timelogs = Timelogs.objects.filter(Q(users_id=usr.id) & Q(endTime__isnull = False))

  paginator = Paginator(timelogs, 25)

  page_number = request.GET.get('page')
  page_obj = paginator.get_page(page_number)
  # pdb.set_trace()
  return render(request, 'user_log_list.html', {'page_obj': page_obj})


@login_required(login_url='/')
def timelogs_list(request):
  timelogs = Timelogs.objects.filter(endTime__isnull = False)

  paginator = Paginator(timelogs, 25)

  page_number = request.GET.get('page')
  page_obj = paginator.get_page(page_number)
  # pdb.set_trace()
  return render(request, 'timelogs-new.html', {'page_obj': page_obj})
