from rest_framework.decorators import api_view
from rest_framework.response import Response
from chatRoom.models import *
from .serializers import *

@api_view(['GET'])
def getRoutes(request):
    Routes=[
        'GET api/',
        'GET api/rooms',
        'GET api/rooms/:id',
    ]
    return Response(Routes)
    #return JsonResponse(Routes, safe=False) #safe=False to allow passing array to JSONresponse

@api_view(['GET'])
def getRooms(request):
    rooms = Room.objects.all()
    serializer = RoomSerializer(rooms, many= True) #many=True: we want many objects to be serialized
    return Response(serializer.data) #it gives the data in the object

@api_view(['GET'])
def getRoom(request, pk):
    room = Room.objects.get(id = pk)
    serializer = RoomSerializer(room, many= False) #many=False: we want a single object to be serialized
    return Response(serializer.data) #it gives the data in the object