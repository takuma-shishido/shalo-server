from django.urls import path
from .views import (
    CardDataList, CardDataDetail, AccountDataList, AccountDataDetail,
    fetch_trending_resources, fetch_account_data, fetch_bookmarks,
    resource_bookmark_by_id, fetch_favorites, fetch_resource_by_id, update_resource_by_id, delete_resource_by_id, fetch_all_resources,
    search_resources, delete_account, create_resource, sign_in, sign_up,
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('v1/cards/', CardDataList.as_view(), name='card-list'),
    path('v1/cards/<str:pk>/', CardDataDetail.as_view(), name='card-detail'),
    path('v1/accounts/', AccountDataList.as_view(), name='account-list'),
    path('v1/accounts/<str:pk>/', AccountDataDetail.as_view(), name='account-detail'),
    path('v1/trending/', fetch_trending_resources, name='fetch-trending-resources'),
    path('v1/account/', fetch_account_data, name='fetch-account-data'),
    path('v1/bookmarks/', fetch_bookmarks, name='fetch-bookmarks'),
    path('v1/favorites/', fetch_favorites, name='fetch-favorites'),
    path('v1/resources/<str:id>/', fetch_resource_by_id, name='fetch-resource-by-id'),
    path('v1/resources/<str:id>/bookmark', resource_bookmark_by_id, name='resource-bookmark-by-id'),
    path('v1/resources/<str:id>/update', update_resource_by_id, name='delete-resource-by-id'),
    path('v1/resources/<str:id>/delete', delete_resource_by_id, name='delete-resource-by-id'),
    path('v1/resources/', fetch_all_resources, name='fetch-all-resources'),
    path('v1/search/', search_resources, name='search-resources'),
    path('v1/delete-account/<str:user_id>/', delete_account, name='delete-account'),
    path('v1/create-resource/', create_resource, name='create-resource'),
    path('v1/sign-in/', sign_in, name='sign-in'),
    path('v1/sign-up/', sign_up, name='sign-up'),
    
    path('v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]