from django.conf.urls import patterns

urlpatterns = patterns('',
    (r'^$', 'wechat.views.index'),
    (r'^post/(?P<post_id>\d+).html$', 'wechat.views.show_post'),
)

