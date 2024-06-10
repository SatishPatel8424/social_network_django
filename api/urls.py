from django.urls import path, include
from .views import LoginView, SearchUserView, FriendRequestView, FriendListView, PendingFriendRequestsView, \
    CustomUserViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register(r'signup', CustomUserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('search/', SearchUserView.as_view(), name='search_user'),
    path('friend-request/', FriendRequestView.as_view(), name='send_friend_request'),
    path('friend-request/<int:pk>/', FriendRequestView.as_view(), name='respond_friend_request'),
    path('friends/', FriendListView.as_view(), name='list_friends'),
    path('pending-requests/', PendingFriendRequestsView.as_view(), name='list_pending_requests'),
]
