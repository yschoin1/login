#-*- coding: utf-8 -*-

from django import forms
from django.contrib.auth.models import User
from .models import nomatUser

# class loginForm(forms.ModelForm):
# 	class Meta:
# 		model = User
# 		widgets = {
#             'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
#             'password': forms.PasswordInput(
#                 attrs={'placeholder': 'Password'}),
#         }
# 		fields = ['email', 'password']

# 	def __init__(self, *args, **kwargs):
#         super(loginForm, self).__init__(*args, **kwargs)
#         self.fields['comment'].error_messages = {'required': '댓글을 적어주세요!'}

# Sign up form
class signUpForm(forms.Form):
	username = forms.CharField(label = '아이디', max_length = 30, error_messages={'required': '아이디를 적어주세요!'})
	email = forms.EmailField(label = '이메일', error_messages={'required': '이메일을 적어주세요!', 'invalid': '유효한 이메일을 적어주세요!'})
	password = forms.CharField(label = '비밀번호', max_length = 50, widget=forms.PasswordInput(), error_messages={'required': '비밀번호를 적어주세요!'})
	reenter = forms.CharField(label = '비밀번호 확인', max_length = 50, widget=forms.PasswordInput(), error_messages={'required': '다시 한번 비밀번호를 적어주세요!'})
	agreeToConditions = forms.BooleanField(label = '아래 내용에 동의합니다.', help_text = '노맛의 목적인 "정보공유와 음식점의 발전을 위한 정당한 비판"에 동의하며 욕설, 악의적인 비방을 하지 않고 음식점에 대한 정당한 비판만을 할 것에 동의함.', error_messages={'required': '노맛을 이용하시려면 약관에 동의해주세요!'})

	# Check if the username is taken
	def clean_username(self):
		username = self.cleaned_data.get('username')
		username = username.encode('utf-8')
		if User.objects.filter(username=username).exists():
			raise forms.ValidationError('이미 "%s"라는 아이디가 존재합니다.' % username)
		return username

	# Check if the email is taken
	def clean_email(self):
		email = self.cleaned_data.get('email')
		email = email.encode('utf-8')
		if User.objects.filter(email = email).exists():
			raise forms.ValidationError('이미 "%s"는 사용중입니다.' % email)
		return email

	# Check if two passwords match
	def clean_reenter(self):
		password = self.cleaned_data.get('password')
		reenter = self.cleaned_data.get('reenter')
		if not password == reenter:
			raise forms.ValidationError("비밀번호가 일치하지 않습니다.")
		return password

# Form to store user data
class nomatUserForm(forms.ModelForm):
	class Meta:
		model = nomatUser
		fields = ['email', 'confirmationCode', 'agreeToConditions']

# Password reset application form
class passwordResetApplicationForm(forms.Form):
	email = forms.EmailField(label = '이메일', widget=forms.TextInput(attrs={'placeholder': 'you@example.com'}))

	# Check if the email exists
	def clean_email(self):
		email = self.cleaned_data.get('email')
		email = email.encode('utf-8')
		if not User.objects.filter(email = email).exists():
			raise forms.ValidationError("등록되지 않은 이메일 주소입니다.")
		return email

# Password reset form
class passwordResetForm(forms.Form):
	password = forms.CharField(label = '새로운 비밀번호', max_length = 50, widget=forms.PasswordInput(), error_messages={'required': '비밀번호를 적어주세요!'})
	reenter = forms.CharField(label = '비밀번호 확인', max_length = 50, widget=forms.PasswordInput(), error_messages={'required': '다시 한번 비밀번호를 적어주세요!'})

	# Check if two passwords match
	def clean_reenter(self):
		password = self.cleaned_data.get('password')
		reenter = self.cleaned_data.get('reenter')
		if not password == reenter:
			raise forms.ValidationError("비밀번호가 일치하지 않습니다.")
		return password

# Sign in form
class signInForm(forms.Form):
	email = forms.EmailField(label = '이메일', widget=forms.TextInput(attrs={'placeholder': 'you@example.com'}))
	password = forms.CharField(label = '비밀번호', widget = forms.PasswordInput())


