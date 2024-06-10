from django.contrib.auth import authenticate
from django.core.paginator import Paginator
from rest_framework import viewsets
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import CustomUser, FriendRequest, Friend
from .serializers import UserSerializer, FriendRequestSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer


class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email', None)
        password = request.data.get('password', None)
        user = CustomUser.objects.filter(email__iexact=email)
        if user.exists():
            if password:
                database_password = user.last().password
                if not database_password:
                    return Response({'message': 'Something went to wrong'}, status=400)
                else:
                    objects = user.last()
                    if objects and objects.check_password(password):
                        user_object = user.last()
                        refresh = RefreshToken.for_user(user_object)
                        data = {
                            'refresh': str(refresh),
                            'access': str(refresh.access_token),
                            'message': "Loging successfully"
                        }
                        return Response(data=data, status=200)
                    else:
                        return Response({'message': 'Entered password is invalid'}, status=400)
            else:
                return Response({'message': 'Please Enter the Password'}, status=400)
        else:
            return Response({'message': 'Email Does Not Exist'}, status=400)


class SearchUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        keyword = request.query_params.get('keyword', '').lower()
        if '@' in keyword:
            users = CustomUser.objects.filter(email__iexact=keyword)
        else:
            users = CustomUser.objects.filter(username__icontains=keyword)
        paginator = Paginator(users, 10)
        page_number = request.query_params.get('page')
        page_obj = paginator.get_page(page_number)
        serializer = UserSerializer(page_obj, many=True)
        return Response(serializer.data)


class FriendRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        receiver_id = request.data.get('receiver_id')
        receiver = CustomUser.objects.get(id=receiver_id)

        # Throttling logic
        one_minute_ago = timezone.now() - timezone.timedelta(minutes=1)
        recent_requests = FriendRequest.objects.filter(sender=request.user, created_at__gte=one_minute_ago).count()
        if recent_requests >= 3:
            return Response({"error": "You can only send 3 friend requests per minute."}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        FriendRequest.objects.create(sender=request.user, receiver=receiver)
        return Response({"message": "Friend request sent"}, status=status.HTTP_201_CREATED)

    def put(self, request, pk):
        friend_request = FriendRequest.objects.get(id=pk)
        action = request.data.get('action')

        if action == 'accept':
            friend_request.status = 'accepted'
            Friend.make_friend(request.user, friend_request.sender)
            Friend.make_friend(friend_request.sender, request.user)  # Make friendship mutual
        elif action == 'reject':
            friend_request.status = 'rejected'
        friend_request.save()
        return Response({"message": f"Friend request {action}ed"}, status=status.HTTP_200_OK)


class FriendListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        friends = Friend.objects.get(current_user=request.user).users.all()
        serializer = UserSerializer(friends, many=True)
        return Response(serializer.data)


class PendingFriendRequestsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        pending_requests = FriendRequest.objects.filter(receiver=request.user, status='pending')
        serializer = FriendRequestSerializer(pending_requests, many=True)
        return Response(serializer.data)
