from django.conf.urls import patterns, include, url

from demo.views import *
from django.contrib import admin
admin.autodiscover()



# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
# Examples:
# url(r'^$', 'cmdb.views.home', name='home'),
# url(r'^cmdb/', include('cmdb.foo.urls')),

# Uncomment the admin/doc line below to enable admin documentation:
# url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

# Uncomment the next line to enable the admin:
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^test/$', test),
                       url(r'^update/$', update),
                       url(r'^line/$', line),
                       url(r'^table/$', table),
                       url(r'^information/$', information),
                       url(r'^$', index),
                       url(r'^login/$', weblogin),
                       url(r'^weblogout/$', weblogout),

)
