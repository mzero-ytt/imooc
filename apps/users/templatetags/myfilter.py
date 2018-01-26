from django import template
register = template.Library()

@register.filter('get_emailerror')
def get_emailerror(dict):
        if dict.get('email',0):
                return dict['email']
        else:
                return None


@register.filter('get_captchaerror')
def get_captchaerror(dict):
        if dict.get('captcha',0):
                return dict['captcha']
        else:
                return None


@register.filter('get_usernameerror')
def get_usernameerror(dict):
        if dict.get('username',0):
                return dict['username']
        else:
                return None


@register.filter('get_passworderror')
def get_passworderror(dict):
        if dict.get('password',0):
                return dict['password']
        else:
                return None

@register.filter('get_password1error')
def get_password1error(dict):
        if dict.get('password1',0):
                return dict['password1']
        else:
                return None

@register.filter('get_password2error')
def get_password2error(dict):
        if dict.get('password2',0):
                return dict['password2']
        else:
                return None

# @register.filter('get_password_merror')
# def get_password_merror(dict):
#         if dict.get('password_m',0):
#                 return dict['password_m']
#         else:
#                 return None

# @register.filter('get_mobileerror')
# def get_mobileerror(dict):
#         if dict.get('mobile',0):
#                 return dict['mobile']
#         else:
#                 return None
# 注册过滤器
# register.filter('month_to_upper', month_to_upper)