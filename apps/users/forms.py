from django import forms
from captcha.fields import CaptchaField

from apps.users.models import UserProfile


# 邮箱注册表单
class RegForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(required=True, min_length=5)
    captcha = CaptchaField()

# 手机注册表单
# class TelephoneForm(forms.Form):
#     mobile = forms.CharField(required=True, min_length=11, max_length=11)
#     password_m = forms.CharField(required=True, min_length=5)
#     captcha = CaptchaField()


# 登录表单
class LoginForm(forms.Form):
    username = forms.CharField(required=True)
    password = forms.CharField(required=True, min_length=5)


# 找回密码表单
class ForgetPwdForm(forms.Form):
    email = forms.EmailField(required=True)
    captcha = CaptchaField()


# 重置密码表单
class ModifyPwdForm(forms.Form):
    password1 = forms.CharField(required=True, min_length=5)
    password2 = forms.CharField(required=True, min_length=5)


# 修改头像表单
class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['image']


# 修改个人信息表单
class ModifyUserInfoForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['nick_name', 'birthday', 'gender', 'address', 'mobile']