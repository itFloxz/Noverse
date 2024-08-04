from django.contrib.auth.models import BaseUserManager
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _

class UserManager(BaseUserManager):
    def email_validator(self,email):
        try:
            validate_email(email)
        except ValidationError:
            raise ValidationError(_("please enter a valid email address"))
        
    def create_user(self, email, first_name, last_name, password, **extra_fileds):
        if email:
            email=self.normalize_email(email)
            self.email_validator(email)
        else:
            raise ValidationError(_("an email address is required"))
        if not first_name:
            raise ValidationError(_("first name is required"))
        if not last_name:
            raise ValidationError(_("last name is required"))
        user = self.model(email=self.normalize_email(email), first_name=first_name, last_name=last_name, **extra_fileds)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, first_name, last_name, password, **extra_fileds):
        extra_fileds.setdefault("is_staff",True)
        extra_fileds.setdefault("is_superuser",True)
        extra_fileds.setdefault("is_verified",True)

        if extra_fileds.get("is_staff") is not True:
            raise ValidationError(_("is staff must be true for admin user"))
        
        if extra_fileds.get("is_superuser") is not True:
            raise ValidationError(_("is superuser must be true for admin user"))
        
        user=self.create_user(
            email, first_name, last_name, password, **extra_fileds
        )
        user.save(using=self._db)
        return user
