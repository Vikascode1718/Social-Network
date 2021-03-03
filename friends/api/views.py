from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from account.api.serializers import PersonSerializer
from account.models import Person, Token

from .serializers import FriendSerializer, FriendRequestSerializer
from friends.models import Friend, FriendRequest

import json
from helpers.api_error_response import errorResponse
import random

# Get user friends
# -----------------------------------------------
@api_view(['GET'])
def getFriends(request):
    try:
        token = request.headers['Authorization'].split()[-1]
    except KeyError:
        return Response(errorResponse("Unauthorized."),status=status.HTTP_401_UNAUTHORIZED)
    person_id = Token.objects.get(token=token).account
    try:
        data = Friend.objects.filter(Q(user_a=person_id) | Q(user_b=person_id))
        friends = [entry.user_a if entry.user_a is not person_id else entry.user_b for entry in data]
        if friends:
            persons = Person.objects.filter(id__in=friends)
            persons_dict = [PersonSerializer(person).data for person in persons]
            return Response(data=dict(friends=persons_dict), status=status.HTTP_200_OK)
        return Response(data=errorResponse("No friends found!"),status=status.HTTP_200_OK)
    except Friend.DoesNotExist:
        return Response(data=errorResponse("No friends found!"),status=status.HTTP_404_NOT_FOUND)

# Get user friend requests
# -----------------------------------------------
@api_view(['GET'])
def getFriendRequests(request):
    try:
        token = request.headers['Authorization'].split()[-1]
    except KeyError:
        return Response(errorResponse("Unauthorized."),status=status.HTTP_401_UNAUTHORIZED)
    
    person_id = Token.objects.get(token=token).account
    
    data = FriendRequest.objects.filter(to_user=person_id)
    friendrequests = []
    if data:
        for fr in data:
            # Check if person exist or if account id deleted
            try:
                persons = Person.objects.get(id=fr.from_user)
                personSerializer = PersonSerializer(persons)
                friendrequests.append({**personSerializer.data, 
                    **{'from_user': fr.from_user, 'to_user': fr.to_user, 'request_id': fr.id,'since':fr.since}})
            except Person.DoesNotExist:
                FriendRequest.objects.get(pk=fr.id).delete()
        return Response(data=dict(requests=friendrequests), status=status.HTTP_200_OK)
    return Response(data=errorResponse("No friend requests!"),status=status.HTTP_200_OK)

# Send friend request to another user
# -----------------------------------------------
@api_view(['POST'])
@csrf_exempt
def sendFriendRequest(request):
    if request.method == 'POST':
        # only need 'to_user' field in post request
        try:
            token = request.headers['Authorization'].split()[-1]
        except KeyError:
            return Response(errorResponse("Unauthorized."),status=status.HTTP_401_UNAUTHORIZED)
        
        req_dict = request.data
        person_id = Token.objects.get(token=token).account

        # Can't send oneself the friend request
        if req_dict['to_user'] != person_id:
            return Response(errorResponse("Cannot send friend request to yourself."),status=status.HTTP_400_BAD_REQUEST)

        # Check if a friend request from a same use to same user has already been made
        try:
            FriendRequest.objects.get(from_user=person_id)
            return Response(errorResponse("Friend request is already sent."),status=status.HTTP_400_BAD_REQUEST)
        except FriendRequest.DoesNotExist:
            # Check if these people are already friends
            try:
                Friend.objects.get(Q(user_a=person_id) & Q(user_b=req_dict['to_user']) | Q(user_a=req_dict['to_user']) & Q(user_b=person_id))
                return Response(errorResponse("You are already friends with the person."),status=status.HTTP_400_BAD_REQUEST)
            except Friend.DoesNotExist:
                req_dict['from_user'] = person_id
                req_dict['since'] = datetime.now().timestamp()
                friendRequestSerializer = FriendRequestSerializer(data=req_dict)
                if friendRequestSerializer.is_valid():
                    friendRequestSerializer.save()
                    return Response(data=friendRequestSerializer.data,status=status.HTTP_201_CREATED)
                else:
                    return Response(friendRequestSerializer.errors,status=status.HTTP_400_BAD_REQUEST)

# Accept friend request
# -----------------------------------------------
@api_view(['PUT'])
def acceptFriendRequest(request):
    try:
        person_token = request.headers['Authorization'].split()[-1]
    except KeyError:
        return Response(errorResponse("Unauthorized."),status=status.HTTP_401_UNAUTHORIZED)
    try:
        person_id = Token.objects.get(token=person_token).account
        print(request.data)
        try:
            friend_request = FriendRequest.objects.get(id=request.data['id'])
            # Check if person responding to the request is the person request is sent to
            if friend_request.to_user == person_id:
                friendSerilizer = FriendSerializer(data=
                        {'user_a':friend_request.from_user, 
                        'user_b': person_id,
                        'since':datetime.now().timestamp()})
                if friendSerilizer.is_valid():
                    friendSerilizer.save()
                    friend_request.delete()
                    # Let's check if users had cross friend requested each other
                    # in that case we need to delete the other request as well
                    res = Response(data=friendSerilizer.data,status=status.HTTP_200_OK)
                    try:
                        duplicate_request= FriendRequest.objects.get(from_user=person_id)
                        duplicate_request.delete()
                    except FriendRequest.DoesNotExist:
                        return res
                    return res
            return Response(errorResponse("Unable to accept friend request."),status=status.HTTP_400_BAD_REQUEST)
        except FriendRequest.DoesNotExist:
            return Response(errorResponse("Friend request is invalid."),status=status.HTTP_400_BAD_REQUEST)
    except Token.DoesNotExist:
        return Response(errorResponse("Session expired, Please log in again!"),status=status.HTTP_400_BAD_REQUEST)


# Log Out function, requires token
# -----------------------------------------------
@api_view(['DELETE'])
def deleteFriendRequest(request):
    try:
        token = request.headers['Authorization'].split()[-1]
        person_id = Token.objects.get(token=token).account
    except [KeyError, Token.DoesNotExist]:
        return Response(errorResponse("Unauthorized."),status=status.HTTP_401_UNAUTHORIZED)
    friend_request = FriendRequest.objects.get(id=request.data['id'])
    if (friend_request.from_user == person_id or friend_request.to_user == person_id):
        friend_request.delete()
        return Response(data=json.loads('{"action": "success"}'),status=status.HTTP_200_OK)
    return Response(errorResponse("Unauthorized."),status=status.HTTP_401_UNAUTHORIZED)

# Friend Suggestions for user
# -----------------------------------------------
@api_view(['GET'])
def getFriendSuggestions(request):
    try:
        token = request.headers['Authorization'].split()[-1]
        person_id = Token.objects.get(token=token).account
    except [KeyError, Token.DoesNotExist]:
        return Response(errorResponse("Unauthorized."),status=status.HTTP_401_UNAUTHORIZED)
    
    # We have some friends
    friends = Friend.objects.filter(Q(user_a=person_id) | Q(user_b=person_id))

    # Let's add our current friends id's in list to  exclude from suggestions
    # and then excluding myself too
    friends_ids = [a.user_b if a.user_a is person_id else a.user_a for a in friends]
    friends_ids.append(person_id)

    persons = list(Person.objects.filter(~Q(id__in=friends_ids)))
    if len(persons) > 0:
        # getting 10 random ids from people we are not friends with
        # and then serializing them and returning them
        random_persons_ids = [a.id for a in random.sample(persons,min(len(persons), 10))]
        random_persons = Person.objects.filter(id__in=random_persons_ids)
        persons_dict = [PersonSerializer(person).data for person in random_persons]
        return Response(data=dict(friend_suggestions=persons_dict), status=status.HTTP_200_OK)
    return Response(errorResponse("No friend suggestions."),status=status.HTTP_204_NO_CONTENT)


# Helper Functions
# -----------------------------------------------