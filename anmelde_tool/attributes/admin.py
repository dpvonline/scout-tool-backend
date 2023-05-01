from django.contrib import admin

from .models import BooleanAttribute, TimeAttribute, IntegerAttribute, FloatAttribute, \
    TravelAttribute, StringAttribute


class BaseAdmin(admin.ModelAdmin):
    list_display = ('name', 'registration')
    search_fields = ('name',)


@admin.register(BooleanAttribute)
class BooleanAttributeAdmin(BaseAdmin):
    pass


@admin.register(TimeAttribute)
class TimeAttributeAdmin(BaseAdmin):
    pass


@admin.register(IntegerAttribute)
class IntegerAttributeAdmin(BaseAdmin):
    pass


@admin.register(FloatAttribute)
class FloatAttributeAdmin(admin.ModelAdmin):
    list_display = ('name', 'registration')
    search_fields = ('name',)


@admin.register(TravelAttribute)
class TravelAttributeAdmin(BaseAdmin):
    pass


@admin.register(StringAttribute)
class StringAttributeAdmin(BaseAdmin):
    pass
