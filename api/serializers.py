from rest_framework import serializers
from .models import CustomUser, FriendRequest


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'password']

    def create(self, validated_data):
        # Extract the password from validated_data and create the user object
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)  # Set the password
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        return super().update(instance, validated_data)


class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ['id', 'sender', 'receiver', 'status', 'timestamp']
        read_only_fields = ['sender', 'status', 'timestamp']
