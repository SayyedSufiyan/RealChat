from django.db.models import Q
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Message
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.db.models import Q
from django.contrib.auth import logout
from django.shortcuts import redirect
from .forms import CustomRegisterForm
from .models import Profile
from .models import FriendRequest
from .utils import send_alert_to_user 


def register_view(request):
    if request.method == 'POST':
        form = CustomRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']
            user.save()

            # Create associated profile
            Profile.objects.create(
                user=user,
                name=form.cleaned_data['name'],
                phone=form.cleaned_data['phone'],
                picture=form.cleaned_data.get('picture')
            )

            login(request, user)

            first_user = User.objects.exclude(id=user.id).first()
            if first_user:
                return redirect('chat_room', user_id=first_user.id)
            else:
                return render(request, 'chat/no_users.html', {'user': user})
    else:
        form = CustomRegisterForm()
    return render(request, 'registration/register.html', {'form': form})





@login_required
def chat_room(request, user_id=None):
    # Get accepted friends only
    friend_reqs = FriendRequest.objects.filter(
        Q(from_user=request.user) | Q(to_user=request.user),
        is_accepted=True
    ).select_related('from_user', 'to_user')

    # Extract friend user IDs
    friend_ids = set()
    for fr in friend_reqs:
        if fr.from_user == request.user:
            friend_ids.add(fr.to_user.id)
        else:
            friend_ids.add(fr.from_user.id)

    # Only show friends in sidebar, preload their profiles
    users = User.objects.filter(id__in=friend_ids).select_related('profile')

    # Unread message count per user
    messages_unread = {
        user.id: Message.objects.filter(
            sender=user,
            receiver=request.user,
            read=False
        ).count()
        for user in users
    }

    # Pending friend requests count (for heart icon)
    friend_request_count = FriendRequest.objects.filter(
        to_user=request.user,
        is_accepted=False
    ).count()

    selected_user = None
    messages = []

    if user_id:
        selected_user = get_object_or_404(User, id=user_id)

        # Ensure selected_user is a friend
        if selected_user.id not in friend_ids:
            return render(request, 'chat/access_denied.html')

        messages = Message.objects.filter(
            Q(sender=request.user, receiver=selected_user) |
            Q(sender=selected_user, receiver=request.user)
        ).order_by('timestamp')

        # Mark received messages as read
        messages.filter(receiver=request.user, read=False).update(read=True)

        # Reset unread count for this user
        messages_unread[selected_user.id] = 0

    return render(request, 'chat/chat_room.html', {
        'users': users,
        'selected_user': selected_user,
        'messages': messages,
        'messages_unread': messages_unread,
        'friend_request_count': friend_request_count,  # ✅ included
    })    # Get accepted friends only
    friend_reqs = FriendRequest.objects.filter(
        Q(from_user=request.user) | Q(to_user=request.user),
        is_accepted=True
    ).select_related('from_user', 'to_user')

    # Extract friend user objects
    friend_ids = set()
    for fr in friend_reqs:
        if fr.from_user == request.user:
            friend_ids.add(fr.to_user.id)
        else:
            friend_ids.add(fr.from_user.id)

    # Only show friends in sidebar, preload their profiles
    users = User.objects.filter(id__in=friend_ids).select_related('profile')

    # Prepare unread message count per user
    messages_unread = {
        user.id: Message.objects.filter(
            sender=user,
            receiver=request.user,
            read=False
        ).count()
        for user in users
    }

    selected_user = None
    messages = []

    if user_id:
        selected_user = get_object_or_404(User, id=user_id)

        # Optional: Ensure selected_user is a friend
        if selected_user.id not in friend_ids:
            return render(request, 'chat/access_denied.html')  # Or handle gracefully

        messages = Message.objects.filter(
            Q(sender=request.user, receiver=selected_user) |
            Q(sender=selected_user, receiver=request.user)
        ).order_by('timestamp')

        # Mark received messages as read
        messages.filter(receiver=request.user, read=False).update(read=True)

        # Reset unread count for that user
        messages_unread[selected_user.id] = 0

    return render(request, 'chat/chat_room.html', {
        'users': users,
        'selected_user': selected_user,
        'messages': messages,
        'messages_unread': messages_unread,
    })


@login_required
def all_users_view(request):
    users = User.objects.exclude(id=request.user.id)

    friends = FriendRequest.objects.filter(
        (Q(from_user=request.user) | Q(to_user=request.user)),
        is_accepted=True
    )

    sent_requests = FriendRequest.objects.filter(
        from_user=request.user,
        is_accepted=False
    )

    # Prepare flat lists of user IDs
    friend_ids = set()
    for fr in friends:
        if fr.from_user == request.user:
            friend_ids.add(fr.to_user.id)
        else:
            friend_ids.add(fr.from_user.id)

    sent_request_ids = sent_requests.values_list('to_user_id', flat=True)

    return render(request, 'chat/all_users.html', {
        'users': users,
        'friend_ids': friend_ids,
        'sent_request_ids': list(sent_request_ids),
    })



@login_required
def profile_view(request):
    profile = Profile.objects.get(user=request.user)
    return render(request, 'chat/profile.html', {
        'user': request.user,
        'profile': profile
    })




def logout_view(request):
    logout(request)
    return redirect('login')



@login_required
def all_users(request):
    users = User.objects.exclude(id=request.user.id)
    sent_requests = FriendRequest.objects.filter(from_user=request.user)
    friends = FriendRequest.objects.filter(
        (models.Q(from_user=request.user) | models.Q(to_user=request.user)),
        is_accepted=True
    )
    return render(request, 'chat/all_users.html', {
        'users': users,
        'sent_requests': sent_requests,
        'friends': friends,
    })

@login_required
def send_friend_request(request, user_id):
    to_user = get_object_or_404(User, id=user_id)
    fr, created = FriendRequest.objects.get_or_create(
        from_user=request.user,
        to_user=to_user
    )
    if created:
        # 📣 Fire off the alert
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"alert_{to_user.id}",
            {
                "type": "send_alert",
                "message": f"{request.user.username} sent you a friend request"
            }
        )
    return redirect("all_users")

@login_required
def notifications(request):
    requests = FriendRequest.objects.filter(to_user=request.user, is_accepted=False)
    return render(request, 'chat/notifications.html', {'requests': requests})

@login_required
def accept_request(request, req_id):
    req = get_object_or_404(FriendRequest, id=req_id, to_user=request.user)
    req.is_accepted = True
    req.save()
    return redirect('notifications')

def send_alert_to_user(user_id, message):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"alert_{user_id}",
        {
            'type': 'send_alert',
            'message': message,
        }
    )