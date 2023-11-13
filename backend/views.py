from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import exceptions, filters, generics, viewsets
from backend.serializers import *
from rest_framework.authtoken.models import Token
from backend.models import *
from rest_framework.permissions import IsAuthenticated, AllowAny
import django_filters.rest_framework
from django.db.models import Value, Case, When, BooleanField, Avg, F, CharField, Prefetch
from backend.filters import DateFilter
from django.db.models.functions import Concat


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer


class VerificationAPIView(APIView):

    def get(self, request, user_key):
        user = MyUser.objects.get(username=user_key)
        user.username = user.email
        user.is_active = True
        user.save()
        return Response({
            'message': 'Email подтвержден.',
        })


class LoginView(generics.CreateAPIView):
    serializer_class = LoginSerializer


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        Token.objects.get(user=request.user).delete()
        return Response("Token is deleted")


class BookListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = BookListSerializer
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend, filters.SearchFilter]
    filterset_class = DateFilter
    search_fields = ['name', ]

    def get_queryset(self):
        favorite_list = [favorite.pk for favorite in self.request.user.favorite.all()]
        queryset = Book.objects.annotate(
            favorite=Case(When(id__in=favorite_list, then=Value(True)), default=Value(False), output_field=BooleanField()),
            url=Concat(Value(f'http://{self.request.get_host()}/books/'), F('slug'), output_field=CharField())
        )
        return queryset


class BookDetailView(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = BookDetailSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        favorite_list = [favorite.pk for favorite in self.request.user.favorite.all()]
        queryset = Book.objects.annotate(
            favorite=Case(When(id__in=favorite_list, then=Value(True)), default=Value(False), output_field=BooleanField())
        )
        return queryset


class BookReviewView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = ReviewSerializer

    def get_queryset(self):
        queryset = Review.objects.filter(author=self.request.user)
        return queryset

    def get(self, request, *args, **kwargs):
        book = Book.objects.prefetch_related(
            Prefetch('reviews', queryset=Review.objects.filter(author=self.request.user))).get(pk=self.kwargs.get('pk'))
        serializer = ReviewGetSerializer(book.reviews.all(), many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        book = Book.objects.prefetch_related(
            Prefetch('reviews', queryset=Review.objects.filter(author=self.request.user))).get(pk=self.kwargs.get('pk'))
        if book.reviews.all().exists():
            return Response('Отзыв уже существует')
        else:
            review = Review.objects.create(author=self.request.user,
                                           rating=serializer.validated_data['rating'],
                                           text=serializer.validated_data['text'])
            book.reviews.add(review)
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        book = Book.objects.prefetch_related(
            Prefetch('reviews', queryset=Review.objects.filter(author=self.request.user))).get(pk=self.kwargs.get('pk'))
        if book.reviews.all().exists():
            instance = book.reviews.all().first()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        else:
            return Response('Отзыв не существует')

    def put(self, request, *args, **kwargs):
        book = Book.objects.get(pk=self.kwargs.get('pk'))
        queryset = self.request.user.favorite.all().values_list('pk', flat=True)
        if book.id in list(queryset):
            self.request.user.favorite.remove(book)
            return Response('Книга удалена из избранного')
        else:
            self.request.user.favorite.add(book)
            return Response('Книга добавлена в избранное')

    def delete(self, request, *args, **kwargs):
        book = Book.objects.prefetch_related(
            Prefetch('reviews', queryset=Review.objects.filter(author=self.request.user))).get(pk=self.kwargs.get('pk'))
        if book.reviews.all().exists():
            book.reviews.get(author=self.request.user).delete()
            return Response('Отзыв удален')
        else:
            return Response('Отзыв не существует')


class FavoriteBookListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = FavoriteBookListSerializer

    def get_queryset(self):
        favorite_list = [favorite.pk for favorite in self.request.user.favorite.all()]
        queryset = Book.objects.filter(id__in=favorite_list)
        return queryset
