#-*- coding: utf-8 -*-

from django.shortcuts import render, redirect
from .forms import signUpForm, passwordResetApplicationForm, passwordResetForm, signInForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import nomatUser
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required

import random, string

# Check to see if the user agreed to the updated conditions of use
def checkForUpdates(request):
	if request.user.is_authenticated():
		nu = nomatUser.objects.get(email = request.user.email)
		if not nu.agreeToConditions:
			return redirect('/updateagreetoconditions')

# Sign in page view
def signIn(request):

	# Check for user condition update
	if checkForUpdates(request):
		return checkForUpdates(request)

	# Get sign in form
	form = signInForm(request.POST or None)

	# Context to display with html
	context = {
		'header': 'Login',
		'title': 'Login',
		'form': form,
		'button': '로그인',
	}

	# Login the user or display proper error messages
	if request.POST:
		email = request.POST['email']
		password = request.POST['password']
		user = authenticate(username = email, password = password)
		if user is not None:
			if user.is_active:
				login(request, user)
				return redirect('/')
			else:
				return render(request, 'jumbotronOnly.html', {
					'header': 'Error',
					'title': '메일 주소로 보낸 이메일을 먼저 확인해 주세요.',
					})
		else:
			if User.objects.filter(email = email).exists():
				return redirect('/passworderror')
			else:
				return render(request, 'jumbotronOnly.html', {
					'header': 'Error',
					'title': '이메일 주소를 다시 한번 확인해 주세요.',
				})

	return render(request, 'form.html', context)

# Sign up page view
def signUp(request):

	# Check if the user is already signed in
	if request.user.is_authenticated():
		return render(request, 'jumbotronOnly.html', {
				'header': 'Error',
				'title': "이미 로그인하신 상태입니다.",
			})

	# Get sign up form
	form = signUpForm(request.POST or None)

	# Context to display with html
	context = {
		'header': 'Register',
		'title': '노맛에 오신걸 환영합니다!',
		'form': form,
		'button': '회원가입',
	}

	# Store user data and send email to confirm email address
	if request.method == 'POST':
		if form.is_valid():
			user = User.objects.create_user(form.cleaned_data['username'], form.cleaned_data['email'], form.cleaned_data['password'])
			user.is_active = False
			user.save()
			confirmationCode = ''.join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for x in range(33))
			nu = nomatUser()
			nu.email = form.cleaned_data['email']
			nu.confirmationCode = confirmationCode
			nu.agreeToConditions = True
			nu.save()

			link = 'http://www.nomat.co.kr/confirm/' + str(confirmationCode) + '/' + user.email

			mail_message = """
안녕하세요, %s님!

nomat 계정 본인 확인 메일입니다. 아래 링크를 클릭하셔서 본인 인증을 완료하여 주십시오.
%s


감사합니다!

nomat팀 드림
			""" % (user.username, link)

			send_mail('[nomat] 계정 인증', mail_message, 'splitterapps@gmail.com', [form.cleaned_data['email']], fail_silently=False)

			return render(request, 'jumbotronOnly.html', {
				'header': 'Register',
				'title': "이메일 주소로 확인 이메일을 보내드렸습니다.",
				'subtitle': "이메일에 포함된 링크를 클릭해서 메일 주소를 확인해주세요!"
			})

	return render(request, 'form.html', context)

# Email confirmation view page
def confirm(request):

	# Get confirmation code embedded in the url
	url = request.get_full_path()
	garbage1, garbage2, confirmationCode, email = url.split('/')

	# See if confirmation codes match
	nu = nomatUser.objects.get(email = email)
	if confirmationCode == nu.confirmationCode:
		user = User.objects.get(email = email)
		user.is_active = True
		user.save()
		context = {
			'title': '노맛의 일원이 되신 것을 환영합니다!',
			'subtitle': '이제 해당 이메일 주소로 로그인이 가능합니다.',
		}
		return render(request, 'jumbotronOnly.html', context)
	else:
		context = {
		'header': 'Error',
		'title': '오류!',
		}
		return render(request, 'jumbotronOnly.html', context)

# Sign out function
def signOut(request):
	logout(request)
	return redirect('/')

# Login required page view
def loginRequired(request):
	return render(request, 'loginRequired.html', {})

# Conditions page view
@login_required()
def agreeToConditions(request):

	# Context to display with html
	context = {
		'title': '이용약관이 새로 생겼습니다.',
		'subtitle': '아래 동의하기 버튼을 눌러 약관에 동의하시고 노맛을 계속 이용하세요!',
		'change': '이용약관 (2015년 8월 25일 기준)',
		'change1': '노맛의 목적인 "정보공유와 음식점의 발전을 위한 정당한 비판"에 동의하며 욕설, 악의적인 비방을 하지 않고 음식점에 대한 정당한 비판만을 할 것에 동의함.',
	}

	# User agrees to the new conditions
	if 'agreeToConditions' in request.POST:
		nu = nomatUser.objects.get(email = request.user.email)
		nu.agreeToConditions = True
		nu.save()
		return redirect('/')

	# Sign out fuction
	if request.method == 'POST':
		if 'signOut' in request.POST:
			return signOutFunc(request)

	return render(request, 'updateagreetoconditions.html', context)

# Error page view function
def passwordError(request):

	# Check if the user is already logged in
	if request.user.is_authenticated():
		return render(request, 'alreadySignedIn.html', {
				'title': "이미 로그인하신 상태입니다."
			})

	# Get password reset application form
	form = passwordResetApplicationForm(request.POST or None)

	# Send confirmation email
	if request.method == 'POST':
		if form.is_valid():
			confirmationCode = ''.join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for x in range(33))
			nu = nomatUser.objects.get(email = form.cleaned_data['email'])
			nu.confirmationCode = confirmationCode
			nu.save()

			link = 'http://www.nomat.co.kr/passwordreset/' + str(confirmationCode) + '/' + form.cleaned_data['email']

			mail_message = """
안녕하세요,

nomat 비밀번호 재설정 요청 메일입니다. 아래 링크를 클릭하셔서 비밀번호를 재설정하여 주십시오.
%s


감사합니다!

nomat팀 드림
			""" % link

			send_mail('[nomat] 비밀번호 재설정 요청', mail_message, 'splitterapps@gmail.com', [form.cleaned_data['email']], fail_silently=False)

			return render(request, 'jumbotronOnly.html', {
				'header': 'Completed',
				'title': "메일 주소로 비밀번호 재설정 이메일을 보내드렸습니다.",
				'subtitle': "이메일에 포함된 링크를 클릭해서 비밀번호를 재설정하세요!",
			})

	# Context to display with html
	context = {
		'header': 'Error',
		'title': '비밀번호를 다시 한번 확인해 주세요.',
		'subtitle': '수많은 비밀번호 기억하기 힘드시죠? 아래에서 재설정하세요!',
		'form': form,
		'button': '보내기',
	}
	
	return render(request, 'form.html', context)

# Password reset page view
def passwordReset(request):

	# Check if the user is already logged in
	if request.user.is_authenticated():
		return render(request, 'alreadySignedIn.html', {
				'title': "이미 로그인하신 상태입니다."
			})

	# Get password reset form
	form = passwordResetForm(request.POST or None)

	# Check url to validate the request
	url = request.get_full_path()
	garbage1, garbage2, confirmationCode, email = url.split('/')
	nu = nomatUser.objects.get(email = email)
	if confirmationCode == nu.confirmationCode:
		context = {
			'header': 'Reset',
			'title': '비밀번호 재설정',
			'form': form,
			'button': '재설정',
		}
	else: 
		context = {
			'header': 'Error',
			'title': '오류',
		}
		return render(request, 'jumbotronOnly.html', context)

	# Store valid password reset request
	if request.method == 'POST':
		if form.is_valid():
			user = User.objects.get(email = email)
			user.set_password(form.cleaned_data['password'])
			user.save()
			context = {
				'title': '비밀번호가 변경되었습니다.',
				'subtitle': '또 까먹으셔도 됩니다! 항상 재설정 하실 수 있으니까요~',
			}
			return render(request, 'jumbotronOnly.html', context)

	return render(request, 'form.html', context)