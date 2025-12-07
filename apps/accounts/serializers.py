from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from rest_framework import serializers
from djoser.serializers import UserSerializer as BaseUserSerializer


User = get_user_model()


class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = ('username', 'email', 'password')


class UserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'date_joined', 'last_login')



class CustomTokenCreateSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, style={'input_type': 'password'}, write_only=True)
    
    default_error_messages = {
        'invalid_credentials': 'Email ou senha incorretos.',
        'inactive_account': 'Conta inativa.',
    }
    
    def validate(self, attrs):
        password = attrs.get('password')
        email = attrs.get('email')
        
        if not email or not password:
            raise serializers.ValidationError(
                self.error_messages['invalid_credentials'],
                code='invalid_credentials',
            )
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                self.error_messages['invalid_credentials'],
                code='invalid_credentials',
            )
        
        if not user.check_password(password):
            raise serializers.ValidationError(
                self.error_messages['invalid_credentials'],
                code='invalid_credentials',
            )
        
        if not user.is_active:
            raise serializers.ValidationError(
                self.error_messages['inactive_account'],
                code='inactive_account',
            )
        
        attrs['user'] = user
        return attrs