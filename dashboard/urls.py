from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import signout,logout,dashboard,loginPage,people,timelogs,transactions,users,people_create_view,transaction_create_view,timelogs_create_view
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('', auth_views.LoginView.as_view(template_name='index.html'), name='login'),
    path('signout/<int:id>/',signout, name='signout'),
    path('logout',logout, name='logout'),
    path('dashboard', dashboard, name='dashboard'),
    path('people', people, name='people'),
    path('people/new', people_create_view, name='people-new'),
    path('timelogs', timelogs, name='timelogs'),
    path('timelogs/new', timelogs_create_view, name='timelogs-new'),
    path('transactions', transactions, name='transactions'),
    path('transactions/new', transaction_create_view, name='transactions-new'),
    path('users', users, name='users'),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)