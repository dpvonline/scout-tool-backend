from django.contrib import admin

from .models import BooleanAttribute, TimeAttribute, IntegerAttribute, FloatAttribute, \
    TravelAttribute, StringAttribute, AttributeEventModuleMapper


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
class FloatAttributeAdmin(BaseAdmin):
    pass


@admin.register(TravelAttribute)
class TravelAttributeAdmin(BaseAdmin):
    pass


@admin.register(StringAttribute)
class StringAttributeAdmin(BaseAdmin):
    pass


@admin.register(AttributeEventModuleMapper)
class AttributeEventModuleMapperAdmin(admin.ModelAdmin):
    list_display = ('id', 'text')
    search_fields = ('event_module',)
