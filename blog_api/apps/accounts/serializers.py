from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for new user registration."""

    password  = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True, label="Confirm password")

    class Meta:
        model  = User
        fields = ("id", "email", "first_name", "last_name", "password", "password2")
        extra_kwargs = {
            "first_name": {"required": False},
            "last_name":  {"required": False},
        }

    def validate(self, attrs):
        if attrs["password"] != attrs.pop("password2"):
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserPublicSerializer(serializers.ModelSerializer):
    """Minimal read-only representation used in nested contexts (e.g., post author)."""

    full_name = serializers.CharField(read_only=True)

    class Meta:
        model  = User
        fields = ("id", "email", "full_name", "avatar")


class UserProfileSerializer(serializers.ModelSerializer):
    """Full profile — used for the authenticated user's own profile."""

    full_name = serializers.CharField(read_only=True)

    class Meta:
        model  = User
        fields = ("id", "email", "first_name", "last_name", "full_name", "bio", "avatar", "date_joined")
        read_only_fields = ("id", "email", "date_joined")


class ChangePasswordSerializer(serializers.Serializer):
    """Allows an authenticated user to change their own password."""

    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, validators=[validate_password])

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Extends the default JWT payload with basic user info."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"]     = user.email
        token["full_name"] = user.full_name
        token["is_staff"]  = user.is_staff
        return token
