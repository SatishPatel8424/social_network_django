from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    groups = models.ManyToManyField(Group, related_name='customuser_set', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='customuser_set', blank=True)


class FriendRequest(models.Model):
    sender = models.ForeignKey(CustomUser, related_name='sent_requests', on_delete=models.CASCADE)
    receiver = models.ForeignKey(CustomUser, related_name='received_requests', on_delete=models.CASCADE)
    status = models.CharField(max_length=20,
                              choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')],
                              default='pending')
    timestamp = models.DateTimeField(auto_now_add=True)


class Friend(models.Model):
    users = models.ManyToManyField(CustomUser)
    current_user = models.ForeignKey(CustomUser, related_name='owner', null=True, on_delete=models.CASCADE)

    @classmethod
    def make_friend(cls, current_user, new_friend):
        friend, created = cls.objects.get_or_create(current_user=current_user)
        friend.users.add(new_friend)

    @classmethod
    def lose_friend(cls, current_user, new_friend):
        friend, created = cls.objects.get_or_create(current_user=current_user)
        friend.users.remove(new_friend)
