from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import *



def LoginView(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        Email = request.POST.get('Email').lower()
        password = request.POST.get('password')
        user = authenticate(request , email = Email, password = password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'User Name or password invalid')
    return render(request, 'chatRoom/LogInOut.html', {'page': page})

def logoutView(request):
    logout(request)
    return redirect('home')


def RegisterView(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = MyUserCreationForm()
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.email = user.email.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occured during registration')
    return render(request, 'chatRoom/LogInOut.html', {'form': form})

def Home(request):
    verify = True
    q = request.GET.get('q')
    if q != None:
        rooms = Room.objects.filter(
            Q(topic__name__icontains = q) |
            Q(name__icontains = q) |
            Q(description__icontains = q)
        ).order_by('-created')

        Room_chats = Message.objects.filter(
            Q(room__topic__name__icontains = q) |
            Q(room__name__icontains = q) |
            Q(room__description__icontains = q)
        ).order_by('-updated')
    else:
        rooms = Room.objects.all().order_by('-created')
        Room_chats = Message.objects.all().order_by('-updated')

    total_rooms = Room.objects.all().count()
    topics = Topic.objects.all()[0:4]
    room_count = rooms.count()
    return render(request ,'chatRoom/Home.html',{'rooms':rooms, 'topics': topics, 'total_rooms':total_rooms,'room_count':room_count , 'Room_chats': Room_chats, 'verify': verify})

def Roomchat(request, pk):
    room = Room.objects.get(id = pk)
    chats = Message.objects.filter(room__id = room.id).order_by('-created')
    # Access the instances of all the users associated with the room (Note: we can do the oposite)
    chat_participants = room.participants.all() 
    if request.method == 'POST':
        Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk = room.id)
    return render(request ,'chatRoom/Room.html',{'room': room, 'chats': chats, 'chat_participants': chat_participants})

def userProfile(request, pk):
    verify = False
    userProfile = User.objects.get(id = pk)
    rooms = Room.objects.filter()
    q = request.GET.get('q')
    if q != None:
        rooms = Room.objects.filter(
            Q(host = userProfile) &
            (
            Q(topic__name__icontains = q) |
            Q(name__icontains = q) |
            Q(description__icontains = q)
            )
        ).order_by('-updated')

        Room_chats = Message.objects.filter(
            Q(user = userProfile) &
            (
            Q(room__topic__name__icontains = q) |
            Q(room__name__icontains = q) |
            Q(room__description__icontains = q)
            )
        ).order_by('-updated')
    else:
        rooms = Room.objects.filter(host = userProfile).order_by('-updated')
        Room_chats = Message.objects.filter(user = userProfile).order_by('-updated')

    total_rooms = Room.objects.filter(host = userProfile).count()
    Room_chats = Message.objects.filter(user = userProfile).order_by('-updated')
    topics = Topic.objects.filter(room__host=userProfile)

    room_count = []
    for topic in topics:
        count = topic.room_set.filter(host=userProfile).count()
        room_count.append((topic, count))
    return render(request, 'chatRoom/Profile.html',{'user' : userProfile, 'Room_chats':Room_chats, 'rooms':rooms, 'topics':topics, 'room_count': room_count, 'total_rooms':total_rooms, 'verify':verify, 'verify_ID': pk})

@login_required(login_url='login')
def editProfile(request,pk):
    user = request.user
    form = UserForm(instance=user)
    if request.method == 'POST': 
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('userProfile', pk = pk)
    return render(request,'chatRoom/editProfile.html',{'form': form})

@login_required(login_url='login')
def addRoom(request):
    verify = True
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name   = topic_name)
        Room.objects.create(
            host = request.user,
            topic = topic,
            name = request.POST.get('name'),
            description = request.POST.get('description')
        )
        return redirect('home')
    return render(request, 'chatRoom/add_room.html', {'form':form, 'topics': topics, 'verify':verify})

@login_required(login_url='login')
def updateRoom(request,pk):
    verify = False
    room = Room.objects.get(id = pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
    if request.user != room.host:
        return HttpResponse('You are not allowed here !!!')
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name   = topic_name)

        room.topic = topic
        room.name = request.POST.get('name')
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')
    return render(request, 'chatRoom/add_room.html',{'form':form,'topics': topics, 'room': room, 'verify':verify})

@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id = pk)
    if request.user != room.host:
        return HttpResponse('You are not allowed here !!!')
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'chatRoom/Delete.html', {'object':room})

@login_required(login_url='login')
def deleteMsg(request, pk):
    msg = Message.objects.get(id = pk)
    room = msg.room
    if request.user != msg.user:
        return HttpResponse('You are not allowed here !!!')
    if request.method == 'POST':
        room.participants.remove(request.user)
        msg.delete()
        return redirect('room', pk = msg.room_id)
    return render(request, 'chatRoom/Delete.html', {'object':msg})

def topicView(request):
    q = request.GET.get('q')
    if q != None:
        topics = Topic.objects.filter(name__icontains = q) 
    else:
        topics = Topic.objects.all()
    total_rooms = Room.objects.all().count()
    
    return render(request,'chatRoom/topics.html', {'total_rooms':total_rooms,'topics':topics})

def activityView(request):
    Room_chats = Message.objects.all().order_by('-updated')
    return render(request, 'chatRoom/activity.html',{'Room_chats':Room_chats})