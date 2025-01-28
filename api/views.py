import datetime
import urllib.parse
import uuid
import jwt
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Q

import pyshorteners.shorteners
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import CardData, User, CardActivity
from .serializers import CardDataSerializer, UserSerializer

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed

from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from linkpreview import link_preview
import time
import urllib.request

service = Service()
options = webdriver.ChromeOptions()
options.add_argument('--headless') 
options.add_argument("--profile-directory=Default")
options.add_argument("--disable-notifications")



driver = webdriver.Chrome(service=service, options=options)
driver.set_window_size(2000, 1000)

def get_site_preview(url, output_path):
    driver.get(url)

    time.sleep(2)
    
    screenshot = driver.get_screenshot_as_png()
    
    with open(output_path, 'wb') as file:
        file.write(screenshot)


def get_user_by_token(token):
    try:
        token = token.split(' ')[1]
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user = User.objects.get(id=payload['id'], email=payload['email'])
        return user
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('Unauthenticated')
    except jwt.DecodeError:
        raise AuthenticationFailed('Unauthenticated')

class CardDataList(generics.ListCreateAPIView):
    queryset = CardData.objects.all()
    serializer_class = CardDataSerializer

class CardDataDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = CardData.objects.all()
    serializer_class = CardDataSerializer

class AccountDataList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class AccountDataDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

@api_view(['GET'])
def fetch_trending_resources(request):
    resources = CardData.objects.all().order_by('rank')
    serializer = CardDataSerializer(resources, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def fetch_account_data(request):
    user = get_user_by_token(request.headers["Authorization"])
    if user:
        bookmarks = user.bookmarksCards.all()
        user.bookmarks = len(bookmarks)
        user.save()

        serializer = UserSerializer(user)
        return Response(serializer.data)
    return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def fetch_bookmarks(request):
    user = get_user_by_token(request.headers["Authorization"])
    bookmarks = user.bookmarksCards.all()
    
    serializer = CardDataSerializer(bookmarks, many=True)

    return Response(serializer.data)

@api_view(['POST'])
def resource_bookmark_by_id(request, id):
    user = get_user_by_token(request.headers["Authorization"])
    try:
        resource = CardData.objects.get(id=id)

        if resource in user.bookmarksCards.all():
            user.bookmarksCards.remove(resource)
            user.bookmarks -= 1
        else:
            user.bookmarksCards.add(resource)
            user.bookmarks += 1

            CardActivity.objects.create(
                id=str(uuid.uuid4()),
                user=user,
                card=resource,
                activityType='bookmark',
                date=datetime.datetime.now().strftime('%Y-%m-%d'),
                time=datetime.datetime.now().strftime('%H:%M:%S')
            )

        user.save()
        return Response(status=status.HTTP_200_OK)
    except CardData.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def fetch_favorites(request):
    favorites = CardData.objects.filter(tags__contains=['favorite'])
    serializer = CardDataSerializer(favorites, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def fetch_resource_by_id(request, id):
    if len(request.headers["Authorization"].split(' ')) == 2:   
        user = get_user_by_token(request.headers["Authorization"])
        try:
            resource = CardData.objects.get(id=id)
            resource.views += 1
            resource.save()

            serializer = CardDataSerializer(resource)

            data = serializer.data 
            if resource in user.bookmarksCards.all():
                data['isBookmarked'] = True
            else:
                data['isBookmarked'] = False
            
            return Response(data)
        except CardData.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
    else:
        try:
            resource = CardData.objects.get(id=id)
            resource.views += 1
            resource.save()

            serializer = CardDataSerializer(resource)

            data = serializer.data 
            data['isBookmarked'] = False

            return Response(data)
        except CardData.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['PUT'])
def update_resource_by_id(request, id):
    user = get_user_by_token(request.headers["Authorization"])
    try:
        resource = CardData.objects.get(id=id)
        
        if resource.author != user.username:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
    
        resource.title = request.data.get('title', resource.title)
        resource.description = request.data.get('description', resource.description)
        resource.save()

        return Response(status=status.HTTP_200_OK)
    except CardData.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
def delete_resource_by_id(request, id):
    user = get_user_by_token(request.headers["Authorization"])
    try:
        resource = CardData.objects.get(id=id)
        if resource.author != user.username:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        resource.delete()

        return Response(status=status.HTTP_200_OK)
    except CardData.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def fetch_all_resources(request):
    resources = CardData.objects.all()
    serializer = CardDataSerializer(resources, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def search_resources(request):
    query = request.query_params.get('query', '')
    query_parts = query.split(' ')
    tag_queries = [part.replace('tag:', '') for part in query_parts if part.startswith('tag:')]
    text_queries = [part for part in query_parts if not part.startswith('tag:')]

    resources = CardData.objects.all()
    if text_queries:
        resources = resources.filter(Q(title__icontains=text_queries[0]) | Q(description__icontains=text_queries[0]))
    if tag_queries:
        resources = resources.filter(tags__contains=tag_queries)

    serializer = CardDataSerializer(resources, many=True)
    return Response(serializer.data)

@api_view(['DELETE'])
def delete_account(request):
    user = get_user_by_token(request.headers["Authorization"])
    user.delete()

@api_view(['POST'])
def create_resource(request):
    user = get_user_by_token(request.headers["Authorization"])

    data = request.data
    resource_id = str(uuid.uuid4())
    data['id'] = resource_id
    data['dateCreated'] = datetime.datetime.now().strftime('%Y-%m-%d')
    data['author'] = user.username

    image_link = link_preview(data['url']).image
    if image_link and image_link.startswith('http'):
        urllib.request.urlretrieve(image_link, f"static/images/{resource_id}.png")
    else:
        get_site_preview(data['url'], f"static/images/{resource_id}.png")
        
    data['previewImage'] = f'http://shalo-api.vta-group.tech/static/images/{resource_id}.png'

    serializer = CardDataSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        user.contributions += 1
        user.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def sign_in(request):
    email = request.data.get('email')
    password = request.data.get('password')

    try:
        account = User.objects.get(email=email)
        if check_password(password, account.password):
            token = jwt.encode({'id': account.id, 'email': account.email}, settings.SECRET_KEY, algorithm='HS256')
            serializer = UserSerializer(account)
            return Response({'accountData': serializer.data, 'token': token})
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def sign_up(request):
    email = request.data.get('email')
    password = request.data.get('password')
    avatar = request.data.get('avatar', '')
    location = request.data.get('location', '')
    website = request.data.get('website', '')
    github = request.data.get('github', '')
    twitter = request.data.get('twitter', '')
    bio = request.data.get('bio', '')

    if User.objects.filter(email=email).exists():
        return Response({'error': 'User already exists'}, status=status.HTTP_400_BAD_REQUEST)
    
    id = str(uuid.uuid4())
    account_data = {
        'id': id,
        'username': request.data.get('username', "user_" + id),
        'email': email,
        'password': password,
        'name':  request.data.get('name', "User_"+ id),
        'avatar': avatar,
        'joinDate': datetime.datetime.now().strftime('%Y-%m-%d'),
        'memberNumber': f'#{User.objects.count() + 1}',
        'contributions': 0,
        'bookmarks': 0,
        'location': location,
        'website': website,
        'github': github,
        'twitter': twitter,
        'bio': bio
    }
    serializer = UserSerializer(data=account_data)
    if serializer.is_valid():
        serializer.save()
        token = jwt.encode({'id': account_data['id'], 'email': account_data['email']}, settings.SECRET_KEY, algorithm='HS256')
        return Response({'accountData': serializer.data, 'token': token}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
