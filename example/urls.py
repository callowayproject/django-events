from django.conf.urls import include, url
from django.views.generic import TemplateView
from django.contrib import admin, auth

from events.views import admin_calendar_view

admin.autodiscover()

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='homepage.html')),
    url(r'^admin/events/calendarview/$', admin_calendar_view),
    url(r'^accounts/signin/$', auth.views.login,
        {'template_name': 'signin.html'}, 'signin'),
    url(r'^accounts/signout/$', auth.views.logout_then_login,
        {'login_url': '/accounts/signin/?signout=True'}, 'signout'),
    url(r'^events/', include('events.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs'
    # to INSTALLED_APPS to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    ]
