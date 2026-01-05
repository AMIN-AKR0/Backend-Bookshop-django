from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, number, username, password, **extra_fields):
        if not number or not username:
            raise ValueError('Users must have an number and a username')

        user  = self.model(number=number, username=username, **extra_fields)
        user.set_password(password)
        user.save()
        return user


    def create_superuser(self, number, username, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Staff must have is_staff=True')

        return self.create_user(number, username, password, **extra_fields)