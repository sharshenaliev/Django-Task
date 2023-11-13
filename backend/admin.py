from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from backend.models import *

admin.site.register(Genre)
admin.site.register(Author)
admin.site.register(Review)


@admin.register(MyUser)
class MyUserAdmin(UserAdmin):
    fieldsets = (('Личная Информация', {'fields': ('username', 'email')}),
                 ('Избранное', {'fields': ('favorite', )}))


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['name', ]
    #readonly_fields = ('reviews', )
    prepopulated_fields = {'slug': ('name',)}