import json

from django.shortcuts import render
from .forms import *
from django.contrib.auth import authenticate, login, logout
from django.views.generic.base import View
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse

from pure_pagination import Paginator, EmptyPage, PageNotAnInteger

from .models import *
from .forms import ImageUploadForm, ModifyUserInfoForm
from apps.operation.models import UserCourse, UserFavorite, UserMessage
from apps.organization.models import CourseOrg, Teacher
from apps.courses.models import Course
from apps.utils.email_send import send_register_email
from apps.utils.mixin_utils import LoginRequiredMixin
# Create your views here.


# 首页
class IndexView(View):
    """
    首页
    """
    def get(self, request):
        all_banners = Banner.objects.all().order_by('index')
        courses = Course.objects.filter(is_banner=False)[:6]
        banner_courses = Course.objects.filter(is_banner=True)[:2]
        course_orgs = CourseOrg.objects.all()[:15]
        return render(request, 'index.html', locals())

# 注册
class RegView(View):
    def get(self, request):
        reg_form = RegForm()
        return render(request, 'register.html', locals())
    def post(self, request):
        reg_form = RegForm(request.POST)
        if reg_form.is_valid():
            user = UserProfile()
            user.email = request.POST.get('email','')
            is_registed = UserProfile.objects.get(email=user.email)
            if is_registed:
                return render(request, 'register.html', {'msg':'该邮箱已经被注册了！','is_registed': is_registed})
            else:
                user.password = make_password(request.POST.get('password'))
                user.is_active =False
                user.save()
                send_register_email(request.POST.get('email'), 'register')
                return render(request, 'login.html')
        else:
            return render(request,'register.html', locals())


# 登录
class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')
    def post(self, request):
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect(reverse('index'))
                else:
                    return render(request, 'login.html', {'msg':'用户没有激活'})
            else:
                return render(request, 'login.html', {'msg':'用户名或者密码错误'})
        else:
            return render(request, 'login.html', locals())

class LoginoutView(View):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect(reverse('index'))


class UserInfoView(LoginRequiredMixin, View):
    """
    用户个人信息
    """
    def get(self, request):
        return render(request, 'usercenter-info.html', locals())

    # 用户修改昵称，手机号，地址，生日
    def post(self, request):
        modifyuserinfo_form = ModifyUserInfoForm(request.POST, instance=request.user)
        res = dict()

        if modifyuserinfo_form.is_valid():
            modifyuserinfo_form.save()
            res['status'] = 'success'
        else:
            res = modifyuserinfo_form.errors
        return HttpResponse(json.dumps(res), content_type='application/json')



class ImageUploadView(View):
    """
    用户修改头像
    """
    def post(self, request):
        # 使用model来修改头像
        # image = request.FILES.get('image', '')
        # request.user.image = image
        # request.user.save()

        # 使用form来修改头像
        # image_form = ImageUploadForm(request.POST, request.FILES)
        # if image_form.is_valid():
        #     image = image_form.cleaned_data['image']
        #     request.user.image = image
        #     request.user.save()

        # 更简便的form方式,由于是继承的是ModelForm，所以他集合了model与form的优点
        image_form = ImageUploadForm(request.POST, request.FILES, instance=request.user)
        res = dict()
        if image_form.is_valid():
            request.user.save()
            res['status'] = 'success'
            res['msg'] = '头像修改成功'
        else:
            res['status'] = 'fail'
            res['msg'] = '头像修改失败'
        return HttpResponse(json.dumps(res), content_type='application/json')


class UpdatePwdView(LoginRequiredMixin, View):
    """
    个人中心修改用户密码
    """
    def post(self, request):
        modify_form = ModifyPwdForm(request.POST)
        res = dict()

        if modify_form.is_valid():
            pwd1 = request.POST.get('password1', '')
            pwd2 = request.POST.get('password2', '')
            if pwd1 != pwd2:
                res['status'] = 'fail'
                res['msg'] = '两次密码不一致'
                return HttpResponse(json.dumps(res), content_type='application/json')
            else:
                user = request.user
                user.password = make_password(pwd1)
                user.save()
                res['status'] = 'success'
                res['msg'] = '密码修改成功'
        else:
            # 注意这两者的区别
            # res['msg'] = modify_form.errors
            res = modify_form.errors
        return HttpResponse(json.dumps(res), content_type='application/json')





class SendEmailCodeView(LoginRequiredMixin, View):
    """
    发送邮箱验证码
    """
    def get(self,request):
        email = request.GET.get('email', '')
        res = dict()
        if UserProfile.objects.filter(email=email):
            res['status'] = 'fail'
            res['msg'] = '邮箱已经被注册了！'
            return HttpResponse(json.dumps(res), content_type='application/json')


class MyCourseView(LoginRequiredMixin, View):
    def get(self, request):
        # 获取该用户的所有课程
        user_courses = UserCourse.objects.filter(user=request.user)
        # 获取这些课程的id
        course_ids = [user_course.course_id for user_course in user_courses]
        # 获取id对应的所有课程
        all_courses = Course.objects.filter(id__in=course_ids)
        return render(request, 'usercenter-mycourse.html', locals())


class MyFavOrgView(LoginRequiredMixin, View):
    def get(self, request):
        myfav_orgs = UserFavorite.objects.filter(user=request.user, fav_type=2)
        org_ids = [ myfav_org.fav_id for myfav_org in myfav_orgs ]
        orgs = CourseOrg.objects.filter(id__in=org_ids)
        return render(request, 'usercenter-fav-org.html', locals())


class MyFavTeacherView(LoginRequiredMixin, View):
    def get(self, request):
        myfav_teachers = UserFavorite.objects.filter(user=request.user, fav_type=3)
        teacher_ids = [ myfav_teacher.fav_id for myfav_teacher in myfav_teachers ]
        teachers = Teacher.objects.filter(id__in=teacher_ids)
        return render(request, 'usercenter-fav-teacher.html', locals())


class MyFavCourseView(LoginRequiredMixin, View):
    def get(self, request):
        myfav_courses = UserFavorite.objects.filter(user=request.user, fav_type=1)
        course_ids = [ myfav_course.fav_id for myfav_course in myfav_courses ]
        courses = Course.objects.filter(id__in=course_ids)
        return render(request, 'usercenter-fav-course.html', locals())


class MyMessageView(LoginRequiredMixin, View):
    def get(self, request):
        all_messages = UserMessage.objects.filter(user=request.user.id)

        # 用户进入个人消息后清空未读消息记录
        unread_messages = all_messages.filter(has_read=False)
        for unread_message in unread_messages:
            unread_message.has_read = True
            unread_message.save()

        # 对消息进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        # Provide Paginator with the request object for complete querystring generation
        p = Paginator(all_messages, request=request, per_page=1)
        messages = p.page(page)
        return render(request, 'usercenter-message.html', locals())


# def page_not_found(request):
#     # 全局404处理函数
#     from django.shortcuts import render_to_response
#     response = render_to_response('404.html', {})
#     # response.status_code = 404
#     return response
#
# def page_error(request):
#     # 全局500处理函数
#     from django.shortcuts import render_to_response
#     response = render_to_response('500.html', {})
#     # response.status_code = 500
#     return response