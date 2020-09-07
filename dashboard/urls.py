from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static
from .views import loadUsers,transactions_complete,people_create_open,signoutPublic,delete_request_public,signin_request,signin,shiftsInRange,django_delete_request,user_report,hours_report,login_report, generate_report, validate_request, generate_email_request,charts,timelogs_delete_request,search_request,user_delete_request,transaction_delete_request,people_edit, timelogs_edit, transactions_edit, delete_request,signout,logout_request,dashboard,loginPage,people,timelogs,transactions,users,people_create_view,transaction_create_view,timelogs_create_view
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', auth_views.LoginView.as_view(template_name='index.html'), name='login'),
    path('loadUsers',loadUsers, name='loadUsers'),
    path('signout/<int:id>/<int:payment>/',signout, name='signout'),
    path('signoutPublic/<int:id>/<int:payment>/',signoutPublic, name='signoutPublic'),
    path('delete/<int:id>/',delete_request, name='delete'),
    path('deletePublic/<int:id>/',delete_request_public, name='deletePublic'),
    path('transaction-delete/<int:id>/',transaction_delete_request, name='transaction-delete'),
    path('timelogs-delete/<int:id>/',timelogs_delete_request, name='timelogs-delete'),
    path('user-delete/<int:id>/',user_delete_request, name='user-delete'),
    path('django-delete/<str:username>/',django_delete_request, name='django-delete'),
    path('logout',logout_request, name='logout'),
    path('dashboard', dashboard, name='dashboard'),
    path('signin', signin, name='signin'),
    path('signin-request', signin_request, name='signin-request'),
    path('people', people, name='people'),
    path('people-create',people_create_open,name='people-create'),
    path('people/new', people_create_view, name='people-new'),
    path('timelogs', timelogs, name='timelogs'),
    path('timelogs/new', timelogs_create_view, name='timelogs-new'),
    path('transactions', transactions, name='transactions'),
    path('edit-transactions/<int:id>/', transactions_edit, name='transactions-edit'),
    path('transactions-complete/<int:id>/', transactions_complete, name='transactions-complete'),
    path('edit-timelogs/<int:id>/', timelogs_edit, name='timelogs-edit'),
    path('transactions/new', transaction_create_view, name='transactions-new'),
    path('edit-people/<int:id>/', people_edit, name='people-edit'),   
    path('users', users, name='users'),
    path('search', search_request, name='search'),
    path('validate', validate_request, name='validate'),
    path('generate-mailing-list', generate_email_request, name='generate-mailing-list'),
    path('generate-report', generate_report, name='generate-report'),
    path('hours-report', hours_report, name='hours-report'),
    path('user-report', user_report, name='user-report'),
    path('login-report', login_report, name='login-report'),
    path('shifts-in-range',shiftsInRange,name='shifts-in-range'),
    path('charts', charts, name='charts'),
    
    
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)