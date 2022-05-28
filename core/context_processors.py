from django.conf import settings
from django.shortcuts import redirect, reverse
import os
# from .utils import SidebarData
# from .models import Config


def core_configurations(request):
    APP_LOGO='%s/%s'%(settings.MEDIA_URL,'company_logo.jpg')
    # confs = Config.objects.filter(is_active=True)
    # company_name=confs.filter(name="company_name").first()
    # logo=confs.filter(name="company_logo").first()
    # favicon=confs.filter(name="company_favicon").first()
    # app_name=confs.filter(name="site_name").first()
    # company_description=confs.filter(name="company_description").first()

    topMenuShortcuts={}
    # Need to test to see if loggged in user has a certain permission
    if request.user.has_perm('users.add_user'):
        topMenuShortcuts['add_user']={'title':'Register User','hx_url':'%s?action=get-form'%(reverse('users'))}
    if request.user.has_perm('pos.add_category'):
        topMenuShortcuts['add_category']={'title':'Register Category','hx_url':'%s?action=get-form'%(reverse('categories'))}
    if request.user.has_perm('pos.add_product'):
        topMenuShortcuts['add_product']={'title':'Register Product','hx_url':'%s?action=get-form'%(reverse('products'))}

    return {
        "APP_NAME": "mPOS",
        "COMPANY_NAME": "mPOS",
        "COMPANY_DESCRIPTION": "Easily manage your sales",
        "APP_LOGO":APP_LOGO,
        "APP_FAVICON":APP_LOGO,
        "WELCOME_VIDEO_URL":"",
        "MODULE":request.session.get("module",""),
        "TOP_MENU_SHORTCUTS":topMenuShortcuts,
        "config":{
            "welcome_video_url":'',
            "welcome_banner":"%s/%s"%(settings.MEDIA_URL,'welcome_banner.jpg'),
            "default_avator":APP_LOGO,
        },
        'INSTALLED_APPS':settings.INSTALLED_APPS
    }
