from django.urls import path
from apps.users import views
from apps.users.views import *

app_name = 'users'
urlpatterns = [
    # 用户信息
    path('info/', UserInfoView.as_view(), name='users_info'),
    # 个人中心修改用户头像
    path('image/upload/', ImageUploadView.as_view(), name='image_upload'),
    # 个人中心修改密码
    path('update/pwd/', UpdatePwdView.as_view(), name='update_pwd'),
    # 个人中心修改邮箱
    path('sendemail_code', UpdatePwdView.as_view(), name='sendemail_code'),
    # 我的课程
    path('mycourse', MyCourseView.as_view(), name='mycourse'),
    # 我收藏的课程机构
    path('myfav/org/', MyFavOrgView.as_view(), name='myfav_org'),
    # 我收藏的授课教师
    path('myfav/teacher/', MyFavTeacherView.as_view(), name='myfav_teacher'),
    # 我收藏的公开课
    path('myfav/course/', MyFavCourseView.as_view(), name='myfav_course'),
    # 我的消息
    path('mymessage/', MyMessageView.as_view(), name='mymessage'),
]

