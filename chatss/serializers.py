from rest_framework import serializers
from .models import GroupChat, accUser , GroupRequest
 # Import your user model

from rest_framework import serializers
from .models import GroupChat

class GroupChatSerializer(serializers.ModelSerializer):
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GroupChat
        fields = ['id', 'name', 'admin', 'vice_admin', 'created_at', 'creator', 'group_picture']
        read_only_fields = ['admin', 'creator', 'created_at']

    def create(self, validated_data):
        user = self.context['request'].user

        # Ensure the creator is set as the admin and added to members
        validated_data['admin'] = user
        validated_data['creator'] = user  # Explicitly set the creator

        # Create the group
        group = GroupChat.objects.create(**validated_data)

        # Add the creator to the members
        group.members.add(user)

        return group



class GroupRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupRequest
        fields = '__all__'
        read_only_fields = ['status', 'created_at']  # Status should be updated via actions, not direct input



class SimpleGroupRequestSerializer(serializers.ModelSerializer):
    sender = serializers.CharField(source='sender.username', read_only=True)
    group = serializers.CharField(source='group.name', read_only=True)

    class Meta:
        model = GroupRequest
        fields = ['sender', 'group', 'created_at']