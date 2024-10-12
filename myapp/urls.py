from django.urls import path
from . import views

urlpatterns = [
    path('', views.landingpage, name='landingpage'),
    path('logout/', views.logout, name='logout'),
    path('land/', views.landingpage, name='landingpage'),
    path('log/', views.log, name='loginpage'),
    path('srt/', views.stortu, name='studentortutor'),
    path('streg/', views.studentreg, name='student_register'),
    path('treg/', views.tutorreg, name='tutor_register'),
    path('sthome/', views.studenthomepage, name='studenthome'),
    path('thome/', views.tutorhome, name='tutorhome'),
    path('adminh/', views.adminhome, name='adminhome'),
    path('admins/', views.adminstudents, name='adminstudents'),
    path('admintu/', views.admintutors, name='admintutors'),
    path('forgotpas/', views.forgotpassword, name='forgotpassword'),
    path('resetpassword/<str:token>/', views.resetpassword, name='resetpassword'),
    path('sthometutors/', views.studenthome_tutors, name='studenthome_tutors'),

    path('stedpro/', views.studenteditprofile, name='studenteditprofile'),
    path('tuedpro/', views.tutoreditprofile, name='tutoreditprofile'),
]
