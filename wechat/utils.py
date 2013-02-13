# coding: utf-8

import re
import json
import random
import datetime

from lxml import etree
from django.http import HttpResponse
from django.db.models import Q
from django.contrib.sites.models import Site

from imtx.apps.blog.models import Post
from imtx.views import aqi_pm25, aqi_category
from wechat.models import WechatUser, Article, MessageResponse

def etree_to_dict(t):
    d = {}
    for t in t.iterchildren():
        d[t.tag] = t.text
    return d

def process_request(request):
    response_xml = ''
    request_dict = etree_to_dict(etree.fromstring(request.raw_post_data))
    # If has no content, save the whole dict to be future process
    request_content = request_dict.get('Content', json.dumps(request_dict))

    user, created = WechatUser.objects.get_or_create(name=request_dict['FromUserName'])
    message_response = MessageResponse.objects.create(user=user,
                                                      request_content=request_content)
    if request_content == 'Hello2BizUser':
        message_response.message_type = 'hello'
        message_response.response_content = u'Hello, 我是TualatriX! 感谢关注IMTX，你可以通过搜索关键字来随机查看我过去写的文章，尝试一下？如: Python。'
        message_response.save()

        response_xml = message_response.build_response_xml()
    elif request_content.isdigit():
        content = int(request_content)
        message_response.response_content = u'AQI: %s, %s' % (aqi_pm25(request_content), aqi_category(aqi_pm25(request_content)))
        message_response.save()

        response_xml = message_response.build_response_xml()
    elif request_content:
        qset = (Q(title__icontains=request_content) | Q(title__icontains=request_content))
        posts = Post.objects.filter(qset, status='publish').distinct()

        if posts:
            post = posts[random.randint(0, posts.count() - 1)]
            article, created = Article.objects.get_or_create(post=post)

            if not created:
                article.count = article.count + 1
                article.save()

            message_response.message_type = 'news'
            message_response.article = article
            message_response.save()

            response_xml = message_response.build_response_xml()
    else:
        message_response.save()

    if response_xml:
        return HttpResponse(response_xml, content_type='application/xml')
    else:
        return HttpResponse('Hello World!')
