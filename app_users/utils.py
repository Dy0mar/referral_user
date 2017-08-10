from django.contrib.auth.models import User as UserGenerate
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from app_users.models import User


def generate_code(length):
    code = UserGenerate.objects.make_random_password(length)
    return code


def update_points(referral_id):
    referral = User.objects.get(id=referral_id)
    current_points = referral.profile.points
    referral.profile.points = current_points + 1
    referral.profile.save()

    if referral.profile.referral_id != 0:
        update_points(referral.profile.referral_id)
    else:
        return True


def sender_mail(username, email, domain, token):
    subject = 'Activate Code'
    message = render_to_string('app_users/account_activation_email.html', {
        'username': username,
        'domain': domain,
        'uid': urlsafe_base64_encode(force_bytes(username)),
        'token': token,
    })
    send_mail(subject, message,
              'from@app.ref', [email], )
