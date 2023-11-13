from django.urls import path, include
from backend.views import *
from rest_framework.routers import DefaultRouter

# router = DefaultRouter()
# router.register('books', BookViewSet, basename='books')


urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('user/<str:user_key>/', VerificationAPIView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('books/', BookListView.as_view()),
    path('books/<str:slug>/', BookDetailView.as_view()),
    path('book/', FavoriteBookListView.as_view()),
    path('book/<int:pk>/', BookReviewView.as_view()),
    #path('', include(router.urls)),
]