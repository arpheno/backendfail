from django.contrib.auth.models import User


class TestcaseUserBackend(object):
    def authenticate(self, user=None,**kwargs):
        return user

    def get_user(self, user_id):
        return User.objects.get(pk=user_id)
