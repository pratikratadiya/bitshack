from django.urls import path
from . import views

urlpatterns = [
	path('', views.signin, name='signin'),
	path('postsign/', views.postsign, name='postsign'),
	path('welcome/', views.welcome, name='welcome'),
	path('logout/', views.logout, name='logout'),
	path('signup/', views.signup, name='signup'),
	path('postsignup/', views.postsignup,name='postsignup'),
	path('addevent/', views.addevent, name='addevent'),
	path('event_create/', views.event_create, name='event_create'),
	path('event_detail/<slug:id>', views.event_detail, name='event_detail'),
	path('gen_pdf/<slug:id>', views.gen_pdf, name='gen_pdf'),
	path('eventdetails/', views.eventdetails, name='eventdetails'),
	path('allreports/', views.allreports, name='allreports'),
	path('raw_access/', views.raw_access, name='raw_access'),
	# path('detect/', views.heart_detect, name='heart_detect'),
	# path('disease_check/', views.disease_check, name='disease_check'),
]