from server.apps.users.logic.request_schemas import UpdateAuthenticatedUserSchema
from server.apps.users.models import UserModel

# Хз, постараюсь сделать по минимуму оверхеда, но хоть было чуть-чуть поддерживаемое


def update_user(data: UpdateAuthenticatedUserSchema, auth_user: UserModel) -> UserModel:
    updated_data = data.model_dump(exclude_unset=True)
    for field, value in updated_data.items():
        setattr(auth_user, field, value)
    auth_user.save()
    return auth_user
