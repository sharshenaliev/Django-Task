from rest_framework import serializers, exceptions
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from backend.models import *
from django.contrib.sites.models import Site
from config.settings import EMAIL_HOST_USER
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.db.models import Avg


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True, validators=[UniqueValidator(queryset=MyUser.objects.all())])
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = MyUser
        fields = ('password', 'password2', 'email')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Пароли не совпадают."})

        return attrs

    def create(self, validated_data):
        username = get_random_string(length=20)
        user = MyUser.objects.create(username=username, email=validated_data['email'], is_active=False)
        user.set_password(validated_data['password'])
        user.save()

        current_site = Site.objects.get_current()
        message = f'https://{str(current_site)}/user/{username}'
        send_mail('Верификация', message, EMAIL_HOST_USER, [user.email,])
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)
    key = serializers.CharField(read_only=True)

    class Meta:
        fields = '__all__'

    def create(self, validated_data):
        user = authenticate(username=validated_data['email'],
                            password=validated_data['password'])
        if not user:
            raise exceptions.AuthenticationFailed('Логин или пароль введен неверно.')
        token, created = Token.objects.get_or_create(user=user)
        return token


class BookListSerializer(serializers.ModelSerializer):
    favorite = serializers.BooleanField()
    rating = serializers.SerializerMethodField()
    url = serializers.CharField()

    class Meta:
        model = Book
        exclude = ('slug', 'description', 'date', 'reviews')

    def get_rating(self, instance):
        num = instance.reviews.all().aggregate(Avg("rating", default=0))
        return num['rating__avg']


class BookDetailSerializer(BookListSerializer):
    url = None
    reviews_data = serializers.SerializerMethodField()

    class Meta:
        model = Book
        exclude = ('slug', )

    def get_reviews_data(self, instance):
        queryset = instance.reviews.values('text', 'rating', 'author')
        return queryset

class ReviewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Review
        exclude = ('author', )


class ReviewGetSerializer(serializers.ModelSerializer):

    class Meta:
        model = Review
        fields = '__all__'


class FavoriteBookListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Book
        exclude = ('slug', 'description', 'date', 'reviews')
