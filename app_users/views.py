from django.contrib import auth
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect
from django.template.context_processors import csrf
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.views.generic import TemplateView

from app_users import utils
from app_users.forms import UserForm, ProfileForm
from app_users.models import User, Profile


def home(request):
    return render(request, 'app_users/home.html')


def register(request):
    context = {}
    context.update(csrf(request))
    template_name = 'app_users/register.html'

    if request.method == 'POST':
        success_url = 'register-success'
        data = request.POST.copy()
        user_form = UserForm(data)
        profile_form = ProfileForm(data)
        username = None

        referral_id = 0
        if 'referral_code' not in data:
            referral_code = None
        else:
            referral_code = data['referral_code']

        if not referral_code:
            referral_count = Profile.objects.filter(referral_id=0).count()
            if referral_count >= 5:
                profile_form.add_error('referral_code', error='referral code is empty')
            else:
                referral_id = 0
        else:
            try:
                username = User.objects.get(profile__referral_code=referral_code)
                referral_id = username.pk
            except User.DoesNotExist:
                profile_form.add_error('referral_code', error='referral code is wrong')
                context['profile_form'] = profile_form
                context['user_form'] = user_form
                return render(request, template_name, context)

        if user_form.is_valid() and profile_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.is_active = False
            new_user.save()

            activation_code = utils.generate_code(20)
            new_profile = profile_form.save(commit=False)
            new_profile.activation_code = activation_code
            new_profile.referral_id = referral_id
            new_profile.referral_code = utils.generate_code(10)

            if referral_id != 0:
                utils.update_points(referral_id)

            new_profile.user = new_user
            new_profile.save()

            utils.sender_mail(new_user.username, new_user.email, get_current_site(request), activation_code)
            return redirect(success_url)

        else:
            context['profile_form'] = profile_form
            context['user_form'] = user_form
            return render(request, template_name, context)
    else:
        referral_count = Profile.objects.filter(referral_id=0).count()
        if referral_count >= 5:
            context['user_form'] = UserForm()
            context['profile_form'] = ProfileForm()
        else:
            context['user_form'] = UserForm()
            context['profile_form'] = []
    return render(request, template_name, context)


def register_success(request):
    if 'HTTP_REFERER' in request.META:
        referrer = request.META['HTTP_REFERER'].split('/')[3]
        if referrer == 'register':
            context = {}
            return render(request, 'app_users/register-success.html', context)
    return redirect('home')


def activate(request, uid64, token):
    try:
        username = force_text(urlsafe_base64_decode(uid64))
        user = User.objects.get(username=username)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user:
        if user.profile.activation_code == token:
            user.is_active = True
            user.save()
            auth.login(request, user)
            return redirect('account')
    else:
        return redirect('home')


class AccountView(TemplateView):
    template_name = 'app_users/account.html'

    def get_context_data(self, **kwargs):
        context = super(AccountView, self).get_context_data(**kwargs)
        context['title'] = 'User Account - SDH'
        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        user = request.user
        user.profile.referral_code = utils.generate_code(10)
        user.save()
        return super(TemplateView, self).render_to_response(context)


def top(request):
    context = {}
    top = User.objects.all().order_by('-profile__points')[:10]
    context['users'] = top
    return render(request, 'app_users/top.html', context)


def login(request):
    context = {}
    context.update(csrf(request))

    if request.user.is_authenticated():
        return redirect('account')

    if request.POST:
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('account')
        else:
            context['login_error'] = 'User not found or no activate'
            return render(request, 'app_users/login.html', context)
    else:
        return render(request, 'app_users/login.html', context)
