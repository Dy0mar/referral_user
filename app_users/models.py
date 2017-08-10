from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    activation_code = models.CharField(max_length=50)
    referral_id = models.IntegerField()
    referral_code = models.CharField(max_length=10, blank=False)
    points = models.IntegerField(default=1)

    def get_referrals(self):
        users = User.objects.filter(profile__referral_id=self.user_id).order_by('id')
        return users

    def get_referred(self):
        if self.referral_id == 0:
            return False
        else:
            return User.objects.get(id=self.referral_id)
