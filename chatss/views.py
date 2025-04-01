from difflib import get_close_matches
from .models import accUser, FriendRequest, FriendList, Profile, Message, Userchannel, GroupChat, GroupRequest
from django.shortcuts import render, redirect , get_object_or_404
from .forms import FriendRequestForm, ProfileForm
from django.contrib.auth import logout as auth_logout
from django.http import JsonResponse
from allauth.account.decorators import verified_email_required
from django.urls import reverse
from django.db.models import Q, Max, Value
from channels.layers import get_channel_layer
from asgiref.sync import sync_to_async , async_to_sync
from django.template.response import TemplateResponse
from django.utils import timezone
from datetime import timedelta
from django.db.models.functions import Substr, Concat
from django.views.decorators.csrf import csrf_exempt
from asgiref.sync import async_to_sync


from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import GroupChatSerializer, GroupRequestSerializer , SimpleGroupRequestSerializer

# ew
def logout(request):
    auth_logout(request)
    return redirect('account_login')

@verified_email_required
def home(request):
    user = request.user
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()

    # Basic device detection
    if 'mobile' in user_agent or 'android' in user_agent or 'iphone' in user_agent:
        template = 'chatss/home.html'
    else:
        template = 'chatss/home_laptop.html'

    return render(request, template, {'user': user})



@verified_email_required
def send_friend_request(request):
    if request.method == 'POST':
        form = FriendRequestForm(request.POST)
        if form.is_valid():
            # Extract the `receiver` field, which is now an `accUser` instance
            receiver = form.cleaned_data['receiver']
            sender = request.user

            # Create or retrieve the friend request
            friend_req, created = FriendRequest.objects.get_or_create(sender=sender, receiver=receiver)
            if created:
                return JsonResponse({'status': 'success', 'message': 'Friend request sent!'})
            else:
                return JsonResponse({'status': 'error', 'message': 'You have already sent a request to this user.'}, status=400)
        else:
            # Extract plain error messages as a list of strings
            error_messages = [error for field_errors in form.errors.values() for error in field_errors]
            # Join errors into a single string to return
            error_message = " ".join(error_messages)

            # Log form errors for debugging
            print("Form errors:", error_message)

            return JsonResponse({'status': 'suggestions', 'errors': error_message})

    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)








@verified_email_required
def accept_friend_request(request, request_id):
    if request.method == "POST":
        try:
            friend_request = FriendRequest.objects.get(id=request_id)
        except FriendRequest.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Friend request not found.'}, status=404)

        if friend_request.receiver == request.user:
            friend_request.accept()
            return JsonResponse({'status': 'accepted'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Unauthorized request.'}, status=403)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)





@verified_email_required
def decline_friend_request(request, request_id):
    if request.method == "POST":
        friend_request = get_object_or_404(FriendRequest, id=request_id)
        if friend_request.receiver == request.user:
            friend_request.decline()
            return JsonResponse({'status': 'declined'})
    return JsonResponse({'status': 'error'}, status=400)



@verified_email_required
def load_friend_requests(request):
    if request.method == "GET":
        friend_requests = FriendRequest.objects.filter(receiver=request.user, is_active=True)
        data = [{
            'id': fr.id, 
            'sender': fr.sender.username, 
            'profile_image': fr.sender.profile.profile_picture.url if fr.sender.profile.profile_picture else None  # Ensure a valid URL or None
        } for fr in friend_requests]
        return JsonResponse({'friend_requests': data})
    return JsonResponse({'status': 'error'}, status=400)





@verified_email_required
def display_friends(request):
    if request.method == "GET":
        try:
            friends_list = request.user.friend_list.friends.all()
            
            data = []
            now = timezone.now()
            
            for friend in friends_list:
                last_online = friend.last_online
                
                # Format last_online
                if last_online.date() == now.date():
                    last_online_str = f"Today at {last_online.strftime('%I:%M %p')}"
                elif last_online.date() == (now - timedelta(days=1)).date():
                    last_online_str = f"Yesterday at {last_online.strftime('%I:%M %p')}"
                else:
                    last_online_str = last_online.strftime('%b %d at %I:%M %p')
                
                data.append({
                    'username': friend.username,
                    'email': friend.email,
                    'id': friend.id,
                    'last_online': last_online_str,  # Add formatted last_online
                })
            
            return JsonResponse({"Friendlist": data}, status=200)
        except FriendList.DoesNotExist:
            return JsonResponse({"error": "Friend list not found"}, status=404)
        


@verified_email_required
@api_view(['GET'])
@permission_classes([AllowAny])
def display_groups(request):
    if request.method == "GET":
        user = request.user

        # Get all groups where the user is a member
        user_groups = GroupChat.objects.filter(members__in=[user])

            # Serialize the groups
        serializer = GroupChatSerializer(user_groups, many=True)

            # Return the serialized data
        return Response(serializer.data, status=status.HTTP_200_OK)
        





@verified_email_required 
def Update_Profile(request):
    profile = request.user.profile  
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()  
            return redirect(reverse('Profile_details', args=[profile.id]))

    else:
        form = ProfileForm(instance=profile)  

    return render(request, 'chatss/update_profile.html', {'form': form})



@verified_email_required
def Profile_info(request, pk):
    # Get the profile based on the username (pk)
    profile = get_object_or_404(Profile, user__username=pk)
    
    # Check if the request user is the owner of the profile
    is_owner = request.user == profile.user
    
    # Prepare the context data
    form = {
        'profile': profile,
        'is_owner': is_owner,  # Pass whether the user is the owner to the template
    }
    
    # Choose the template based on whether the user is the owner
    if is_owner:
        template_name = 'chatss/profile_info_owner.html'  # Template for the owner
    else:
        template_name = 'chatss/profile_info_other.html'  # Template for someone else

    return render(request, template_name, form)

    


async def Chat_to_Person(request, id):
    # Fetch the person and current user asynchronously
    person = await sync_to_async(accUser.objects.get)(id=id)
    me = request.user

    # Fetch messages between the current user and the person asynchronously
    messages = await sync_to_async(lambda: list(Message.objects.filter(
        Q(from_who=me, to_who=person) | Q(to_who=me, from_who=person)
    ).order_by('timestamp')))()
    
    try:
        # Fetch the user's channel name asynchronously
        user_channel_name = await sync_to_async(Userchannel.objects.get)(user=person)
        
        # Prepare data to send to the channel
        data = {
            "type": "receiver_function", 
            "type_of_data": "the_messages_has_been_seen_from_the_other"
        }

        # Get the channel layer and send data asynchronously
        channel_layer = get_channel_layer()
        await channel_layer.send(user_channel_name.Channelname, data)

        # Update the messages asynchronously to mark them as seen
        await sync_to_async(lambda: Message.objects.filter(
            from_who=person, to_who=me
        ).update(has_been_seen=True))()

    except Userchannel.DoesNotExist:
        print(f"Error: {person} has no channel to receive messages.")

    # Format timestamps for messages
    now = timezone.now()
    formatted_messages = []
    for message in messages:
        timestamp = message.timestamp
        time_difference = now - timestamp

        if time_difference < timedelta(days=1):
            # If the message was sent today
            formatted_time = timestamp.strftime("%I:%M %p")  # Example: 03:15 PM
            formatted_timestamp = f"Today {formatted_time}"
        elif time_difference < timedelta(days=2):
            # If the message was sent yesterday
            formatted_time = timestamp.strftime("%I:%M %p")  # Example: 10:30 PM
            formatted_timestamp = f"Yesterday {formatted_time}"
        else:
            # For older messages, show the full date
            formatted_timestamp = timestamp.strftime("%b %d, %Y %I:%M %p")  # Example: Oct 25, 2023 08:45 AM


    

        formatted_messages.append({
            "message": message,
            "formatted_timestamp": formatted_timestamp
        })


    context = {
        "person": person,
        "me": me, 
        "messages": formatted_messages,  # Use the formatted messages
    }

    # Return a TemplateResponse asynchronously
    return TemplateResponse(request, "chatss/chat_person.html", context)

@verified_email_required 
def home_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'User not authenticated'}, status=401)

    user = request.user

    # Get all users who sent or received a message from/to the current user
    message_friends_ids = Message.objects.filter(
        Q(from_who=user) | Q(to_who=user)
    ).values_list('from_who', 'to_who').distinct()

    # Flatten the list of tuples and remove duplicates
    message_friends_ids = set(
        [item for sublist in message_friends_ids for item in sublist if item != user.id]
    )

    # Get the user details
    message_friends = accUser.objects.filter(id__in=message_friends_ids)

    last_messages = Message.objects.filter(
        Q(from_who__in=message_friends_ids, to_who=user) |
        Q(from_who=user, to_who__in=message_friends_ids)
    ).annotate(
        latest_message=Max('timestamp'),
        truncated_content=Concat(
            Substr('message', 1, 17),  # Truncate to 17 characters
            Value('...')               # Add ellipsis
        )
    ).order_by('-timestamp')
    # Organize data
    data = []
   

    for friend in message_friends:
        # Get the latest message involving this friend
        last_message = last_messages.filter(
            Q(from_who=friend, to_who=user) |
            Q(from_who=user, to_who=friend)
        ).first()

        last_online = friend.last_online
        now = timezone.now()

        # Format last_online
        if last_online.date() == now.date():
            last_online_str = f"Today at {last_online.strftime('%I:%M %p')}"
        elif last_online.date() == (now - timedelta(days=1)).date():
            last_online_str = f"Yesterday at {last_online.strftime('%I:%M %p')}"
        else:
            last_online_str = last_online.strftime('%b %d at %I:%M %p')

        # Format last_message_timestamp (same logic as last_online)
        if last_message:
            last_message_timestamp = last_message.timestamp
            if last_message_timestamp.date() == now.date():
                last_message_timestamp_str = f"Today at {last_message_timestamp.strftime('%I:%M %p')}"
            elif last_message_timestamp.date() == (now - timedelta(days=1)).date():
                last_message_timestamp_str = f"Yesterday at {last_message_timestamp.strftime('%I:%M %p')}"
            else:
                last_message_timestamp_str = last_message_timestamp.strftime('%b %d at %I:%M %p')
        else:
            last_message_timestamp_str = ""

        data.append({
            'username': friend.username,
            'email': friend.email,
            'id': friend.id,
            'picture': friend.profile.profile_picture.url,
            'last_message': last_message.message[:17] + '...' if last_message and len(last_message.message) > 20 else last_message.message if last_message else None,
            'last_message_timestamp': last_message_timestamp_str,
            'last_online': last_online_str,
        })

    return JsonResponse({'message_friends': data})



@csrf_exempt
def chat_to_person_api(request, id):
    if request.method != "GET":
        return JsonResponse({"error": "Invalid request method"}, status=400)
    
    # Fetch the person synchronously
    person = accUser.objects.get(id=id)
    me = request.user

    # Fetch messages synchronously
    messages = list(
        Message.objects.filter(
            Q(from_who=me, to_who=person) | Q(to_who=me, from_who=person)
        ).select_related("from_who", "to_who").order_by("timestamp")
    )
    
    try:
        # Fetch user channel synchronously
        user_channel_name = Userchannel.objects.get(user=person)
        
        # Prepare data for WebSocket notification
        data = {
            "type": "receiver_function",
            "type_of_data": "the_messages_has_been_seen_from_the_other"
        }
        
        # Send data synchronously via channel layer
        channel_layer = get_channel_layer()
        try:
            async_to_sync(channel_layer.send)(user_channel_name.Channelname, data)
        except Exception as e:
            print(f"Error sending message to channel layer: {e}")
        
        # Mark messages as seen synchronously
        Message.objects.filter(from_who=person, to_who=me).update(has_been_seen=True)
    except Userchannel.DoesNotExist:
        print(f"Error: {person} has no channel to receive messages.")
    
    # Format timestamps
    now = timezone.now()
    formatted_messages = [
        {
            "message": msg.message,
            "from_who": msg.from_who.id,
            "to_who": msg.to_who.id,
            "formatted_timestamp": (
                f"Today {msg.timestamp.strftime('%I:%M %p')}" if now - msg.timestamp < timedelta(days=1) else
                f"Yesterday {msg.timestamp.strftime('%I:%M %p')}" if now - msg.timestamp < timedelta(days=2) else
                msg.timestamp.strftime("%b %d, %Y %I:%M %p")
            ),
            "has_been_seen": msg.has_been_seen,
        }
        for msg in messages
    ]

    response_data = {
        "person": {
            "id": person.id,
            "username": person.username,
            "profile_picture": person.profile.profile_picture.url if hasattr(person, "profile") and person.profile.profile_picture else None,
            "last_online": person.last_online.strftime("%b %d, %Y, %I:%M %p"),
            "bio": person.profile.bio,
            "age":  person.age,
            "gender": "Male" if person.gender == "M" else "Female"
        },
        "me": {
            "id": me.id,
            "username": me.username,
        },
        "messages": formatted_messages,
    }

    return JsonResponse(response_data, safe=False)





@csrf_exempt
def group_chat_api(request, group_id):
    if request.method != "GET":
        return JsonResponse({"error": "Invalid request method"}, status=400)
    
    try:
        group = GroupChat.objects.get(id=group_id)
    except GroupChat.DoesNotExist:
        return JsonResponse({"error": "Group not found"}, status=404)
    
    me = request.user
    if me not in group.members.all():
        return JsonResponse({"error": "You are not a member of this group"}, status=403)

    messages = list(
        Message.objects.filter(group=group)
        .select_related("from_who")
        .order_by("timestamp")
    )

    channel_layer = get_channel_layer()
    group_members_channels = Userchannel.objects.filter(user__in=group.members.all())

    data = {
        "type": "receiver_function",
        "type_of_data": "group_messages_updated"
    }

    for member_channel in group_members_channels:
        if member_channel.user != me:  
            try:
                async_to_sync(channel_layer.send)(member_channel.Channelname, data)
            except Exception as e:
                print(f"Error sending message to channel layer: {e}")

    # Format timestamps
    now = timezone.now()
    formatted_messages = [
        {
            "message": msg.message,
            "from_who": msg.from_who.username,
            "formatted_timestamp": (
                f"Today {msg.timestamp.strftime('%I:%M %p')}" if now - msg.timestamp < timedelta(days=1) else
                f"Yesterday {msg.timestamp.strftime('%I:%M %p')}" if now - msg.timestamp < timedelta(days=2) else
                msg.timestamp.strftime("%b %d, %Y %I:%M %p")
            ),
        }
        for msg in messages
    ]

    response_data = {
        "group": {
            "id": group.id,
            "name": group.name,
            "admin": group.admin.username if group.admin else None,
            "vice_admin": group.vice_admin.id if group.vice_admin else None,
            "created_at": group.created_at.strftime("%b %d, %Y, %I:%M %p"),
            "group_avatar": group.group_picture.url,
        },
        "me": {
            "id": me.id,
            "username": me.username,
            "is_admin_or_vice": me == group.admin or me == group.vice_admin,
        },
        "messages": formatted_messages,
    }

    return JsonResponse(response_data, safe=False)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_group(request):
    """
    Create a new group. The request user will be set as the admin and creator.
    """
    serializer = GroupChatSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        group = serializer.save(creator=request.user, admin=request.user)
        group.members.add(request.user)  # Ensure creator is added to members
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_group_details(request, pk):
    """
    Retrieve details of a specific group.
    """
    group = get_object_or_404(GroupChat, pk=pk)
    serializer = GroupChatSerializer(group)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def transfer_admin(request, pk):
    """
    Transfer admin rights to another group member.
    Only the current admin can perform this action.
    """
    group = get_object_or_404(GroupChat, pk=pk)

    if request.user != group.admin:
        return Response({"error": "Only the admin can transfer admin rights."}, status=status.HTTP_403_FORBIDDEN)

    new_admin_id = request.data.get("new_admin_id")
    new_admin = group.members.filter(pk=new_admin_id).first()

    if not new_admin:
        return Response({"error": "The new admin must be a member of the group."}, status=status.HTTP_400_BAD_REQUEST)

    group.admin = new_admin
    group.save()
    
    return Response({"message": "Admin transferred successfully."}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def received_group_requests(request):
    """Returns group requests received by the authenticated user."""
    requests = GroupRequest.objects.filter(receiver=request.user, status='pending')
    serializer = SimpleGroupRequestSerializer(requests, many=True)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([AllowAny])
def send_group_request(request):
    """
    Only the admin or vice admin of a group can send a request.
    """
    group_id = request.data.get("group_id")
    receiver_name = request.data.get("receiver_name")

    # Validate required data
    if not group_id or not receiver_name:
        return Response({"error": "Missing group_id or receiver_name"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        group = GroupChat.objects.get(id=group_id)
    except GroupChat.DoesNotExist:
        return Response({"error": "Group not found"}, status=status.HTTP_404_NOT_FOUND)

    try:
        receiver = accUser.objects.get(username=receiver_name)
    except accUser.DoesNotExist:
        # Suggest similar usernames if the receiver is not found
        all_usernames = list(accUser.objects.values_list("username", flat=True))
        suggestions = get_close_matches(receiver_name, all_usernames, n=3, cutoff=0.6)
        
        return Response({
            "error": "Receiver not found",
            "suggestions": suggestions
        }, status=status.HTTP_404_NOT_FOUND)

    # Ensure the sender is the admin or vice admin
    if request.user != group.admin and request.user != group.vice_admin:
        return Response({"error": "Only the admin or vice admin can send requests"}, status=status.HTTP_403_FORBIDDEN)

    # Prevent duplicate requests
    if GroupRequest.objects.filter(group=group, sender=request.user, receiver=receiver, status="pending").exists():
        return Response({"error": "Request already sent"}, status=status.HTTP_400_BAD_REQUEST)

    # Create the request
    group_request = GroupRequest.objects.create(group=group, sender=request.user, receiver=receiver)
    return Response(GroupRequestSerializer(group_request).data, status=status.HTTP_201_CREATED)





@api_view(["POST"])
@permission_classes([IsAuthenticated])
def handle_group_request(request, request_id, action):
    """
    Accept or reject a group request.
    """
    try:
        group_request = GroupRequest.objects.get(id=request_id)
    except GroupRequest.DoesNotExist:
        return Response({"error": "Request not found"}, status=status.HTTP_404_NOT_FOUND)

    # Ensure only the receiver can accept/reject
    if request.user != group_request.receiver:
        return Response({"error": "You are not authorized to respond to this request"}, status=status.HTTP_403_FORBIDDEN)

    if action == "accept":
        group_request.accept()
    elif action == "reject":
        group_request.reject()
    else:
        return Response({"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)

    return Response(GroupRequestSerializer(group_request).data, status=status.HTTP_200_OK)
