from typing import TYPE_CHECKING

from django.contrib.auth import get_user_model
from ninja.security import HttpBasicAuth

if TYPE_CHECKING:
    from server.apps.users.models import UserModel
else:
    UserModel = get_user_model()


class BasicAuth(HttpBasicAuth):

    def authenticate(self, request, username, password) -> UserModel | None:
        try:
            user = UserModel.objects.get(**{UserModel.USERNAME_FIELD: username})
        except UserModel.DoesNotExist:
            return None
        if not user.check_password(password):
            return None
        return user
