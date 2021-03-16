from django.db.models import Q

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from datetime import datetime
from helpers.error_messages import UNAUTHORIZED, INVALID_TOKEN, INVALID_REQUEST
from helpers.api_error_response import errorResponse

from friends.models import Friend
from account.models import Person, Token
from posts.models import Comment, Posts

from .serializers import CommentSerializer
from account.api.serializers import PersonSerializer

# Get all post comments
# By default it requires user to be logged in and be friends with post author
@api_view(['GET'])
def getPostComments(request, post):
    person = getPersonID(request)
    if type(person) is Response:
        return person

    author = getAuthor(post)
    if type(author) is Response:
        return author

    if isFriends(author.id, person) or author.id == person:
        # Person can only retrieve comments if they are friends with author or author themselves
        result = [{
                **comment,
                'person':PersonSerializer(Person.objects.get(id=comment['person_id'])).data
            } for comment in Comment.objects.filter(post_id=post).values()]
        return Response({"comments":result},status=status.HTTP_200_OK)

    return Response(errorResponse(INVALID_REQUEST),status=status.HTTP_400_BAD_REQUEST)

# Post a new comment on a post
# Requires commentator to be friends with post author
# ---------------------------------------------------
@api_view(['POST'])
def postNewComment(request, post_id):
    person = getPersonID(request)
    if type(person) is Response:
        return person
    
    post = getPost(post_id)
    if type(post) is Response:
        return post
    time_stamp = datetime.now().timestamp()

    # Filtering
    if post.person_id != person:
        # post author themselves are not commenting on their post
        if isFriends(post.person_id, person) == False:
            # post author and person trying to comment are not friends
            # if they are friends then we let the commentator post a comment
            return Response(errorResponse(INVALID_REQUEST), status=status.HTTP_400_BAD_REQUEST)
    
    commentSerializer = CommentSerializer(data={
        'post_id':post.id,
        'person_id':person,
        'comment_text':request.data['comment_text'],
        'comment_parent':request.data['comment_parent'],
        'created': time_stamp,
        'updated': time_stamp
    })
    if commentSerializer.is_valid():
        commentSerializer.save()
        return Response(data=commentSerializer.data, status=status.HTTP_201_CREATED)
    return Response(commentSerializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT','DELETE','POST'])
def actionsComment(request):
    return Response(errorResponse(INVALID_REQUEST),status=status.HTTP_400_BAD_REQUEST)

# Helper Functions
# *********************************************
def getPersonID(request):
    try:
        token = request.headers['Authorization'].split()[-1]
    except KeyError:
        return Response(errorResponse(UNAUTHORIZED),status=status.HTTP_401_UNAUTHORIZED)
    try:
        return Token.objects.get(token=token).account
    except Token.DoesNotExist:
        return Response(errorResponse(INVALID_TOKEN),status=status.HTTP_400_BAD_REQUEST)

def isFriends(person_a, person_b):
    try:
        Friend.objects.get(Q(user_a=person_a) & Q(user_b=person_b) | Q(user_a=person_b) & Q(user_b=person_a))
        return True
    except Friend.DoesNotExist:
        return False

def getAuthor(post):
    # getAuthor returns a person model
    try:
        post_author_id = Posts.objects.get(id=post).person_id
        try:
            return Person.objects.get(id=post_author_id)
        except Person.DoesNotExist:
            return Response(errorResponse(INVALID_REQUEST),status=status.HTTP_400_BAD_REQUEST)
    except Posts.DoesNotExist:
        return Response(errorResponse(INVALID_REQUEST),status=status.HTTP_400_BAD_REQUEST)

def getPost(post):
    try:
        return Posts.objects.get(id=post)
    except Posts.DoesNotExist:
        return Response(errorResponse(INVALID_REQUEST),status=status.HTTP_400_BAD_REQUEST)
