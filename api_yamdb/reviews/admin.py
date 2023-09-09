from django.contrib import admin

from reviews.models import Comment, Review, Title, Genre, Category


admin.site.register(Title)
admin.site.register(Comment)
admin.site.register(Review)
admin.site.register(Genre)
admin.site.register(Category)
