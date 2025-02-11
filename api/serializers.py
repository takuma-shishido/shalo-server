from rest_framework import serializers
from .models import CardData, User

class CardDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardData
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
