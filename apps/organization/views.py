import json

from django.shortcuts import render
from django.views.generic.base import View
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse  # 可以指明我们返回给用户是什么类型的数据
from django.db.models import Q

from .models import *
from .forms import UserAskForm
from apps.courses.models import *
from apps.operation.models import *
# Create your views here.



class OrgView(View):
    '''
    课程机构列表功能
    '''
    def get(self, request):
        # 课程机构
        all_orgs = CourseOrg.objects.all()
        # 取出热门机构
        hot_orgs = all_orgs.order_by('-click_nums')[:3]
        # 城市
        all_cities = CityDict.objects.all()

        # 机构搜索功能
        search_keywords = request.GET.get('keywords', '')
        if search_keywords:
            all_orgs = all_orgs.filter(Q(name__icontains=search_keywords)|Q(desc__icontains=search_keywords))

        # 取出筛选机构
        category = request.GET.get('ct', '')
        if category:
            all_orgs = all_orgs.filter(category=category)

        # 排序
        sort = request.GET.get('sort', '')
        if sort:
            if sort == 'students':
                all_orgs = all_orgs.order_by('-students')
            elif sort == 'courses':
                all_orgs = all_orgs.order_by('-course_nums')


        # 取出筛选城市
        city_id = request.GET.get('city', '')
        if city_id:
            all_orgs = all_orgs.filter(city_id=city_id)

        # 对课程机构进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        # Provide Paginator with the request object for complete querystring generation
        p = Paginator(all_orgs, request=request, per_page=3)
        orgs = p.page(page)
        return render(request, 'org-list.html', locals())


# class AddUserAskView(View):
#     """
#     用户添加咨询（异步）
#     """
#     def post(self, request):
#         userask_form = UserAskForm(request.POST)
#         if userask_form.is_valid():
#             # 使用ModelForm的好处就是可以直接.save()保存，commit=True，指的是直接保存，而不是只是提交
#             user_ask = userask_form.save(commit=True)
#             return HttpResponse("{'status':'success'}", content_type='application/json') # content_type告诉浏览器返回的是什么类型的数据
#         else:
#             return HttpResponse("{'status':'fail', 'msg':'添加出错'}", content_type='application/json')

# 用户添加咨询课程表单提交
class AddUserAskView(View):
    def post(self, request):
        user_ask_form = UserAskForm(request.POST)
        res = dict()
        if user_ask_form.is_valid():
            user_ask_form.save(commit=True)
            res['status'] = 'success'
        else:
            res['status'] = 'fail'
            res['msg'] = '添加错误'
        return HttpResponse(json.dumps(res), content_type='application/json')


class OrgHomeView(View):
    """
    机构首页
    """
    def get(self, request, org_id):
        current_page = 'home'
        course_org = CourseOrg.objects.get(id=int(org_id))
        course_org.click_nums += 1
        course_org.save()
        # 初始化判断是否收藏
        has_fav = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True
        all_courses = course_org.course_set.all()[:3]
        all_teachers = course_org.teacher_set.all()[:1]
        return render(request, 'org-detail-homepage.html', locals())


class OrgCourseView(View):
    """
    机构课程列表页
    """
    def get(self, request, org_id):
        current_page = 'course'
        course_org = CourseOrg.objects.get(id=int(org_id))
        # 初始化判断是否收藏
        has_fav = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True
        all_courses = course_org.course_set.all()
        return render(request, 'org-detail-course.html', locals())


class OrgDescView(View):
    """
    机构简介页面
    """
    def get(self, request, org_id):
        current_page = 'desc'
        course_org = CourseOrg.objects.get(id=int(org_id))
        # 初始化判断是否收藏
        has_fav = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True
        return render(request, 'org-detail-desc.html', locals())


class OrgTeacherView(View):
    """
    机构讲师页面
    """
    def get(self, request, org_id):
        current_page = 'teacher'
        course_org = CourseOrg.objects.get(id=int(org_id))
        # 初始化判断是否收藏
        has_fav = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True
        all_teachers = course_org.teacher_set.all()
        return render(request, 'org-detail-teachers.html', locals())


class AddFavView(View):
    """
    用户收藏, 用户取消收藏
    """
    # 收藏数的增减
    def set_fav_nums(self, fav_type, fav_id, num=1):
        if int(fav_type) == 1:
            course = Course.objects.get(id=fav_id)
            course.fav_nums += num
            course.save()
        elif int(fav_type) == 2:
            course_org = CourseOrg.objects.get(id=fav_id)
            course_org.fav_nums += num
            course_org.save()
        elif int(fav_type) == 3:
            teacher = Teacher.objects.get(id=fav_id)
            teacher.fav_nums += num
            teacher.save()


    def post(self, request):
        fav_id = request.POST.get('fav_id', 0)  # 这里要注意了，因为想要的是数字类型的字符串，所以要填0，方便后面的int转化，不然会出错的
        fav_type = request.POST.get('fav_type', 0)

        res = dict()
        # 判断用户是否登陆
        if request.user.is_authenticated:
            # 查询收藏记录
            exist_records = UserFavorite.objects.filter(user=request.user, fav_id=int(fav_id), fav_type=int(fav_type))
            if exist_records:
                # 记录已经存在，则表示用户取消收藏
                exist_records.delete()
                self.set_fav_nums(fav_type=fav_type, fav_id=fav_id, num=-1)
                res['status'] = 'success'
                res['msg'] = '收藏'
            else:
                user_fav = UserFavorite()
                if fav_id and fav_type:
                    user_fav.user = request.user
                    user_fav.fav_id = fav_id
                    user_fav.fav_type = fav_type
                    user_fav.save()

                    self.set_fav_nums(fav_type=fav_type, fav_id=fav_id, num=1)

                    res['status'] = 'success'
                    res['msg'] = '已收藏'
                else:
                    res['status'] = 'fail'
                    res['msg'] = '收藏出错'
            return HttpResponse(json.dumps(res), content_type='application/json')
        else:
            res['status'] = 'fail'
            res['msg'] = '用户未登录'
            return HttpResponse(json.dumps(res), content_type='application/json')


class TeacherListView(View):
    def get(self, request):
        all_teachers = Teacher.objects.all()

        # 教师搜索功能
        search_keywords = request.GET.get('keywords', '')
        if search_keywords:
            all_teachers = all_teachers.filter(Q(name__icontains=search_keywords))

        # 对教师进行排序
        sort = request.GET.get('sort', '')
        if sort:
            if sort == 'hot':
                all_teachers = all_teachers.order_by('-click_nums')

        # 对教师列表进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        # Provide Paginator with the request object for complete querystring generation
        p = Paginator(all_teachers, request=request, per_page=1)
        teachers = p.page(page)

        # 讲师排行榜
        top_teachers = all_teachers.order_by('-click_nums')
        return render(request, 'teachers-list.html', locals())


class TeacherDetailView(View):
    def get(self, request, teacher_id):
        teacher = Teacher.objects.get(pk=teacher_id)
        teacher.click_nums += 1
        teacher.save()
        teacher_courses = Course.objects.filter(teacher=teacher).all()

        # 教师所有课程进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        # Provide Paginator with the request object for complete querystring generation
        p = Paginator(teacher_courses, request=request, per_page=1)
        courses = p.page(page)

        # 教师所属机构
        teacher_org = CourseOrg.objects.get(teacher=teacher)

        # 判断初始化的用户收藏状态
        has_fav_org = False
        has_fav_teacher = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=teacher.id, fav_type=3):
                has_fav_teacher = True
            if UserFavorite.objects.filter(user=request.user, fav_id=teacher_org.id, fav_type=2):
                has_fav_org = True


        # 讲师排行榜
        all_teachers = Teacher.objects.all()
        top_teachers = all_teachers.order_by('-click_nums')
        return render(request, 'teacher-detail.html', locals())


