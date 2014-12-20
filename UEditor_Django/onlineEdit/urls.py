from django.conf.urls import patterns, include, url

from django.contrib import admin
import os

admin.autodiscover()

ROOT = os.path.dirname(__file__)

urlpatterns = patterns('',
                       # Examples:
                       url(r'^$', 'onlineEdit.views.ueTest', {"template": "ueTest.html"}),
                       # url(r'^blog/', include('blog.urls')),
                       url(r'ueTest', 'onlineEdit.views.ueTest', {"template": "ueTest.html"}),
                       ( r'^UE/(?P<path>.*)$', 'django.views.static.serve',
                         {'document_root': (ROOT + "/UE").replace('\\', '/')}
                       ),

)