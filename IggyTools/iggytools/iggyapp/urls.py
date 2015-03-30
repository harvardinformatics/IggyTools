from django.conf.urls import patterns, include, url
from iggytools.iggyapp import views
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mysite.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$|^seqstats$', views.index, name='index'),
    url(r'^seqstats/test_minilims|^test_minilims', views.testMinilims, name='test_minilims'),
    url(r'^seqstats/minilims|^minilims', views.minilims, name='minilims'),
    url(r'^seqstats/ml_plot_test|^ml_plot_test', views.minilimsPlotTest, name='minilims_plot_test'),
    url(r'^seqstats/getldata|^getldata', views.getLData, name='get_ldata'),
    url(r'^seqstats/showrorl|^showrorl', views.showRorL, name='show_run'),
    url(r'^seqstats/admin/', include(admin.site.urls)),
    url(r'^admin/', include(admin.site.urls)),
)
