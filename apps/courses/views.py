import json

from django.shortcuts import render
from django.views.generic.base import View
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.db.models import Q

from .models import *
from apps.operation.models import *
from apps.utils.mixin_utils import LoginRequiredMixin

# Create your views here.


class CourseListView(View):
    def get(self, request):
        all_courses = Course.objects.all().order_by('-add_time')
        # 排序
        sort = request.GET.get('sort', '')

        # 课程搜索功能
        search_keywords = request.GET.get('keywords', '')
        if search_keywords:
            all_courses = all_courses.filter(Q(name__icontains=search_keywords)|Q(desc__icontains=search_keywords)|Q(detail__icontains=search_keywords))

        if sort:
            # 热门排序
            if sort == 'hot':
                current_page = 'hot'
                all_courses = Course.objects.all().order_by('-click_nums')
            # 参与人数排序
            else:
                current_page = 'students'
                all_courses = Course.objects.all().order_by('-students')

        # 对公开课进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        # Provide Paginator with the request object for complete querystring generation
        p = Paginator(all_courses, request=request, per_page=6)
        courses = p.page(page)

        # 热门课程
        hot_courses = Course.objects.all().order_by('-fav_nums')[:3]

        return render(request, 'course-list.html', locals())


class CourseDetailView(View):
    def get(self, request, course_id):
        course = Course.objects.get(pk=course_id)
        # 增加课程点击数
        course.click_nums += 1
        course.save()

        # 课程/机构收藏
        has_fav_course = False
        has_fav_org = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course.id, fav_type=1):
                has_fav_course = True
            if UserFavorite.objects.filter(user=request.user, fav_id=course.course_org.id, fav_type=2):
                has_fav_org = True

        # 找到相关课程
        tag = course.tag
        if tag:
            relate_courses = Course.objects.filter(tag=tag)[:1]
        else:
            tag = []
        return render(request, 'course-detail.html', locals())


class CourseInfoView(LoginRequiredMixin, View):
    def get(self, request, course_id):
        course = Course.objects.get(pk=course_id)
        course.students +=1
        course.save()

        # 判断用户之前是否加入过课程
        is_joined = UserCourse.objects.filter(user=request.user, course=course)
        if not is_joined:
            user_course = UserCourse()
            user_course.user = request.user
            user_course.course = course
            user_course.save()

        # 得出学过该课程的同学还学过的课程
        # 获取学习过该课程的所有用户
        course_users = UserCourse.objects.filter(course=course)
        # 获取用户id
        user_ids = [course_user.user.id for course_user in course_users ]
        # 获取用户学习过的所有课程
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        # 取出所有课程的id
        course_ids = [user_course.course.id for user_course in all_user_courses]
        relate_courses = Course.objects.filter(id__in=course_ids).order_by('-click_nums')[:3]
        all_resources = CourseResource.objects.filter(course=course)
        return render(request, 'course-video.html', locals())


class CourseCommentView(LoginRequiredMixin, View):
    def get(self, request, course_id):
        course = Course.objects.get(pk=course_id)
        all_resources = CourseResource.objects.filter(course=course)
        all_comments = CourseComments.objects.all()

        # 获取学习过该课程的所有用户
        course_users = UserCourse.objects.filter(course=course)
        # 获取用户id
        user_ids = [course_user.user.id for course_user in course_users]
        # 获取用户学习过的所有课程
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        # 取出所有课程的id
        course_ids = [user_course.course.id for user_course in all_user_courses]
        relate_courses = Course.objects.filter(id__in=course_ids).order_by('-click_nums')[:3]

        return render(request, 'course-comment.html', locals())

class AddCommentView(View):
    def post(self, request):
        # 判断用户登陆状态
        res = dict()
        if not request.user.is_authenticated:
            res['status'] = 'fail'
            res['msg'] = '用户未登录'
            return HttpResponse(json.dumps(res), content_type='application/json')

        course_id = request.POST.get('course_id', 0)
        comments = request.POST.get('comments', '')
        if course_id and comments:
            course_comments = CourseComments()
            course_comments.course = Course.objects.get(id=course_id)
            course_comments.comments = comments
            course_comments.user = request.user
            course_comments.save()
            res['status'] = 'success'
            res['msg'] = '添加成功'
        else:
            res['status'] = 'fail'
            res['msg'] = '添加失败'

        return HttpResponse(json.dumps(res), content_type='application/json')


# 课程信息
class VideoPlayView(LoginRequiredMixin, View):
    """
    视频播放页面
    """
    def get(self, request, video_id):
        video = Video.objects.get(id=video_id)
        course = video.lesson.course

        # 判断用户之前是否加入过课程
        is_joined = UserCourse.objects.filter(user=request.user, course=course)
        if not is_joined:
            user_course = UserCourse()
            user_course.user = request.user
            user_course.course = course
            user_course.save()

        # 得出学过该课程的同学还学过的课程
        # 获取学习过该课程的所有用户
        course_users = UserCourse.objects.filter(course=course)
        # 获取用户id
        user_ids = [course_user.user.id for course_user in course_users]
        # 获取用户学习过的所有课程
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        # 取出所有课程的id
        course_ids = [user_course.course.id for user_course in all_user_courses]
        relate_courses = Course.objects.filter(id__in=course_ids).order_by('-click_nums')[:3]
        all_resources = CourseResource.objects.filter(course=course)
        return render(request, 'course-play.html', locals())