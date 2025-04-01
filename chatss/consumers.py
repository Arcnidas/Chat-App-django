from asgiref.sync import async_to_sync , sync_to_async
from chatss.models import accUser, Message, Userchannel, GroupChat
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils.timezone import now
import json
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope.get("user")
        if not user.is_authenticated:
            await self.close()
            return

        await self.accept() 

        # Try to get or create the Userchannel for the user
        user_channel, created = await Userchannel.objects.aget_or_create(
            user=user,
            defaults={"Channelname": self.channel_name}
        )
        if not created:
            user_channel.Channelname = self.channel_name
            await user_channel.asave()


        self.person_id = self.scope.get("url_route").get("kwargs").get("id")
        print(self.person_id)

    async def receive(self, text_data):
        text_data = json.loads(text_data)
        print("Received data:", text_data)

        other_user = await accUser.objects.aget(id=self.person_id)
        print("Other user:", other_user)

        if text_data.get("type") == "new_message":
            message_content = text_data.get("message", "").strip()  # Trim whitespace and remove empty lines

            # Validate the message content
            if not message_content:
                print("Error: Message is empty or contains only whitespace.")
                return  # Stop further processing

            # Create and save the message
            new_message = Message()
            current_time = now()
            date = current_time.date()
            time = current_time.time()

            new_message.from_who = self.scope.get("user")
            new_message.to_who = other_user
            new_message.message = message_content  # Use the validated message content
            new_message.date = date
            new_message.time = time
            new_message.has_been_seen = False
            await new_message.asave()

            print("Message saved:", new_message.message)

            try:
                user_channel_name = await Userchannel.objects.aget(user=other_user)

                # Prepare data to send to the other user
                data = {
                    "type": "receiver_function",
                    "type_of_data": "new_message",
                    "data": message_content  # Send the validated message content
                }

                # Send message to the other user's channel
                await self.channel_layer.send(user_channel_name.Channelname, data)
                print(f"Message sent to {user_channel_name.Channelname}")

            except Userchannel.DoesNotExist:
                print(f"Error: {other_user} has no channel to receive messages.")

        elif text_data.get("type") == "I_have_seen_the_messages":
            try:
                user_channel_name = await Userchannel.objects.aget(user=other_user)
                data = {
                    "type": "receiver_function",
                    "type_of_data": "the_messages_has_been_seen_from_the_other"
                }

                await self.channel_layer.send(user_channel_name.Channelname, data)

                # Update the seen status of messages
                await Message.objects.filter(
                    from_who=other_user, to_who=self.scope.get("user")
                ).aupdate(has_been_seen=True)

                print(f"Seen status sent to {user_channel_name.Channelname}")

            except Userchannel.DoesNotExist:
                print("Error: No channel found for seen status.")

    async def receiver_function(self, the_data_that_will_come):
        print(f"Data received by receiver_function: {the_data_that_will_come}")
        data = json.dumps(the_data_that_will_come)
        await self.send(data)



# consumers.p

from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from .models import GroupChat, Message
from asgiref.sync import sync_to_async
import json

User = get_user_model()

class GroupChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if self.user.is_authenticated:
            self.group_id = self.scope['url_route']['kwargs']['group_id']
            self.group_name = f'group_{self.group_id}'

            # Add the user to the group's channel layer group
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json.get("message", "").strip()  # Ensure message is valid
        except (json.JSONDecodeError, TypeError):
            return  # Ignore invalid JSON

        if not message:  # Ignore empty messages
            return

        group = await GroupChat.objects.aget(id=self.group_id)
        is_member = await sync_to_async(group.members.filter(id=self.user.id).exists)()

        if is_member:
            message_obj = await Message.objects.acreate(
                from_who=self.user,
                group=group,
                message=message,
                timestamp=now()
            )

            # Broadcast message to the group (excluding the sender)

        def format_timestamp(timestamp):
            now = datetime.now()
            today = now.date()
            yesterday = today - timedelta(days=1)

            if timestamp.date() == today:
                return timestamp.strftime("Today %H:%M")
            elif timestamp.date() == yesterday:
                return timestamp.strftime("Yesterday %H:%M")
            else:
                return timestamp.strftime("%Y-%m-%d %H:%M")

        # Example usage within your group_send function
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'chat_message',
                'message': message,
                'from_user': self.user.username,
                'timestamp': format_timestamp(message_obj.timestamp),
                'sender_channel_name': self.channel_name  # Include sender's channel name
            }
        )


    async def chat_message(self, event):
        # Exclude the sender from receiving the message
        if event['sender_channel_name'] != self.channel_name:
            await self.send(text_data=json.dumps({
                'type': 'chat_message',
                'message': event['message'],
                'from_user': event['from_user'],
                'timestamp': event['timestamp']
            }))