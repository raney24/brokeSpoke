from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import search_request,user_delete_request,transaction_delete_request,people_edit, timelogs_edit, transactions_edit, delete_request,signout,logout_request,dashboard,loginPage,people,timelogs,transactions,users,people_create_view,transaction_create_view,timelogs_create_view
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('', auth_views.LoginView.as_view(template_name='index.html'), name='login'),
    path('signout/<int:id>/',signout, name='signout'),
    path('delete/<int:id>/',delete_request, name='delete'),
    path('transaction-delete/<int:id>/',transaction_delete_request, name='transaction-delete'),
    path('user-delete/<int:id>/',user_delete_request, name='user-delete'),
    path('logout',logout_request, name='logout'),
    path('dashboard', dashboard, name='dashboard'),
    path('people', people, name='people'),
    path('people/new', people_create_view, name='people-new'),
    path('timelogs', timelogs, name='timelogs'),
    path('timelogs/new', timelogs_create_view, name='timelogs-new'),
    path('transactions', transactions, name='transactions'),
    path('edit-transactions/<int:id>/', transactions_edit, name='transactions-edit'),
    path('edit-timelogs/<int:id>/', timelogs_edit, name='timelogs-edit'),
    path('transactions/new', transaction_create_view, name='transactions-new'),
    path('edit-people/<int:id>/', people_edit, name='people-edit'),   
    path('users', users, name='users'),
     path('search', search_request, name='search'),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)