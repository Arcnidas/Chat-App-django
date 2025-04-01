from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, Group, Permission
from django.utils import timezone
from chatss.managers import CustomUserManager

class FriendList(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="friend_list")
    friends = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="friends_of")

    def __str__(self):
        return self.user.username

    def add_friend(self, accUser):
        if accUser not in self.friends.all():
            self.friends.add(accUser)

    def remove_friend(self, accUser):
        if accUser in self.friends.all():
            self.friends.remove(accUser)

    def unfriend(self, removee):
        self.remove_friend(removee)
        friends_list = FriendList.objects.get(user=removee)
        friends_list.remove_friend(self.user)

    def is_mutual_friend(self, friend):
        return friend in self.friends.all()


class FriendRequest(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_requests")
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="received_requests")
    is_active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username}"

    def accept(self):
        try:
            receiver_friend_list = FriendList.objects.get(user=self.receiver)
        except FriendList.DoesNotExist:
            receiver_friend_list = FriendList.objects.create(user=self.receiver)
        
        receiver_friend_list.add_friend(self.sender)

        try:
            sender_friend_list = FriendList.objects.get(user=self.sender)
        except FriendList.DoesNotExist:
            sender_friend_list = FriendList.objects.create(user=self.sender)
        
        sender_friend_list.add_friend(self.receiver)

        self.is_active = False
        self.save()


    def decline(self):
        self.is_active = False
        self.save()

    def cancel(self):
        self.is_active = False
        self.save()


class accUser(AbstractBaseUser, PermissionsMixin):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )

    username = models.CharField(max_length=100, blank=False, null=False)
    email = models.EmailField(max_length=254, blank=False, null=False, unique=True)
    password = models.CharField(max_length=128, blank=False, null=False)  

    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    last_online = models.DateTimeField(null=True, blank=True)

    groups = models.ManyToManyField(
        Group,
        related_name='accuser_set',  
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='accuser_set',  
        blank=True
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"] 

    objects = CustomUserManager()

    def __str__(self):
        return self.username
 

class RelatedModel(models.Model):
    acc_user = models.ForeignKey(accUser, on_delete=models.SET_NULL, null=True, blank=True)
    # Other fields

class Profile(models.Model):
    user = models.OneToOneField(accUser,on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pics/',default='profile_pictures/base_profile.png')
    bio = models.TextField(max_length=500, blank=True)
    from_signal= models.BooleanField(default= False)

    def __str__(self):
        return f"{self.user.username}'s Profile" 

# Assuming accUser is your custom user model

class GroupChat(models.Model):
    name = models.CharField(max_length=255)
    members = models.ManyToManyField(accUser, related_name='group_members')
    admin = models.ForeignKey(accUser, on_delete=models.CASCADE, related_name='created_groups', null=True)
    vice_admin = models.ForeignKey(accUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='vice_admin_groups')
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(accUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_groups_creator')
    group_picture = models.ImageField(upload_to='group_pictures/',default='group_pictures/Default_group.svg')
    def __str__(self):
        return self.name

    def can_send_request(self, user):
        # Only the admin and vice admin can send group requests
        return user == self.admin or user == self.vice_admin

    def transfer_admin(self, new_admin):
        """
        Transfer admin rights to another user.
        """
        if new_admin in self.members.all():
            self.admin = new_admin
            self.save()
        else:
            raise ValueError("The new admin must be a member of the group.")

class GroupRequest(models.Model):
    group = models.ForeignKey(GroupChat, on_delete=models.CASCADE, related_name='group_requests')
    sender = models.ForeignKey(accUser, on_delete=models.CASCADE, related_name='sent_group_requests')
    receiver = models.ForeignKey(accUser, on_delete=models.CASCADE, related_name='received_group_requests')
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username} ({self.group.name})"

    def accept(self):
        self.status = 'accepted'
        self.group.members.add(self.receiver)
        self.save()

    def reject(self):
        self.status = 'rejected'
        self.save()

class Message(models.Model):
    from_who = models.ForeignKey(accUser, default=None, on_delete=models.CASCADE, related_name="sent_messages")
    to_who = models.ForeignKey(accUser, null=True, blank=True, on_delete=models.CASCADE, related_name="received_messages")  # Direct messages only
    group = models.ForeignKey(GroupChat, null=True, blank=True, on_delete=models.CASCADE, related_name="messages")  # Group messages only
    message = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    has_been_seen = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.to_who and self.group:
            raise ValueError("A message cannot be both a direct and group message.")
        super().save(*args, **kwargs)

    def is_group_message(self):
        return self.group is not None

    def __str__(self):
        if self.group:
            return f"{self.from_who.username} -> Group: {self.group.name}"
        elif self.to_who:
            return f"{self.from_who.username} -> {self.to_who.username}"
        return "Invalid Message"




class Userchannel(models.Model):
    user = models.ForeignKey(accUser,on_delete=models.CASCADE, default=None)
    Channelname = models.TextField(null=True, blank=True)
 
