from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required

from app_users import views

urlpatterns = [
    url(r'^$', views.home, name='home'),

    url(r'^register/$', views.register, name='register'),

    url(r'^register-success/$', views.register_success, name='register-success'),
    url(r'^activate/(?P<uid64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),

    url(r'^account/$', login_required(views.AccountView.as_view(), login_url='login'), name='account', ),
    url(r'^top10/$', login_required(views.top), name='top10'),

    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': 'login'}, name='logout'),

]
