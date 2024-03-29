from rest_framework import serializers
from .models.User import User
from .models.UserSession import UserSession
from .models.CharterHistory import CharterHistory

class CurrentUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'id', 'is_premium', 'searches_left', 'max_searches')

class UserSessionSerializer(serializers.ModelSerializer):
    # session_id = serializers.UUIDField(format='hex')
    # for_key = serializers.UUIDField(format='hex', source='for_key.id')
    class Meta:
        model = UserSession
        fields = ('searches_left', 'session_id',)

class CharterHistorySerializer(serializers.ModelSerializer):
    # session_id = serializers.UUIDField(format='hex')
    # for_key = serializers.UUIDField(format='hex', source='for_key.id')
    class Meta:
        model = CharterHistory
        fields = ('flights_number', 'departure_city', 'arrival_city')