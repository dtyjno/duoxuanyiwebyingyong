from django import forms
from .models import User  # 假设 User 模型在 models.py 中定义
from captcha.fields import CaptchaField, CaptchaTextInput

class LoginForm(forms.Form):
    username = forms.CharField(label="用户名", max_length=100)
    password = forms.CharField(label="密码", widget=forms.PasswordInput())

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    captcha = CaptchaField(label='验证码', widget=CaptchaTextInput(attrs={'class': 'form-control'}), error_messages={'invalid': '验证码错误'})

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', '两次输入的密码不一致')

        return cleaned_data
