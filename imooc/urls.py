"""imooc URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import xadmin
from django.urls import path, include, re_path
from django.views.static import serve


from imooc.settings import MEDIA_ROOT

from apps.users.views import *

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegView.as_view(), name='register'),
    # path('active/<str:active_code>/', ActiveUserView.as_view(), name='user_active'),
    # path('forgetpwd/', ForgetPwdView.as_view(), name='forgetpwd'),
    # path('resetpwd/<str:active_code>/', ResetPwdView.as_view(), name='resetpwd'),
    # path('modifypwd/', ModifyPwdView.as_view(), name='modifypwd'),
    path('loginout/', LoginoutView.as_view(), name='loginout'),

    # path('admin/', admin.site.urls),
    path('xadmin/', xadmin.site.urls),
    path('captcha/', include('captcha.urls')),
    path('org/', include('apps.organization.urls', namespace='org')),
    path('course/', include('apps.courses.urls', namespace='course')),
    path('users/', include('apps.users.urls', namespace='users')),
    # 配置上传文件的访问处理函数
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': MEDIA_ROOT}),
    # re_path(r'^static/(?P<path>.*)$', serve, {'document_root': STATIC_ROOT}),
    # re_path(r'^ueditor/',include('DjangoUeditor.urls' )),
]




