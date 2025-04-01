from django.contrib import admin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import FriendList, FriendRequest, accUser , Profile, Userchannel, Message, GroupChat, GroupRequest
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

# Register the Friendship model

class FriendListAdmin(admin.ModelAdmin):
    list_filter =['user']
    list_display=['user']
    search_fields = ['user']
    readonly_fields = ['user']

    class Meta:
        model=FriendList

admin.site.register(FriendList,FriendListAdmin)
admin.site.register(Userchannel)
admin.site.register(Message)
admin.site.register(GroupChat)
admin.site.register(GroupRequest)

class FriendRequestAdmin(admin.ModelAdmin):
    list_filter =['sender','receiver']
    list_display=['sender','receiver']
    search_fields = ['sender__username','sender__email','receiver__username','receiver__email']
    
    class Meta:
        model = FriendRequest

admin.site.register(FriendRequest,FriendRequestAdmin)  






class UserAdmin(BaseUserAdmin):
    # The fields to be used in displaying the User model.
    list_display = ('email', 'username', 'age', 'gender', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_active', 'gender')
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('username', 'age', 'gender')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('date_joined',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'age', 'gender', 'password1', 'password2'),
        }),
    )
    search_fields = ('email', 'username')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)

admin.site.register(accUser, UserAdmin)


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('bio', 'profile_picture', 'user') 

    def profile_picture_tag(self, obj):
        if obj.profile_picture:
            return format_html(f'<img src="{obj.profile_picture.url}" width="50" height="50" />')
        return 'No Image'

    profile_picture_tag.short_description = 'Profile Picture'  # Name for admin display

admin.site.register(Profile, ProfileAdmin)