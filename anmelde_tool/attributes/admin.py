# from django.contrib import admin
# from polymorphic.admin import PolymorphicChildModelAdmin, PolymorphicParentModelAdmin, PolymorphicChildModelFilter
#
# from .models import AbstractAttribute, BooleanAttribute, TimeAttribute, IntegerAttribute, FloatAttribute, \
#     TravelAttribute, StringAttribute
#
#
# class AbstractAttributeChildAdmin(PolymorphicChildModelAdmin):
#     """ Base admin class for all child models """
#     base_model = AbstractAttribute  # Optional, explicitly set here.
#     list_display = ('name', 'type', 'template')
#     search_fields = ('name', 'type')
#     autocomplete_fields = ('type',)
#     show_in_index = True
#
#
# @admin.register(BooleanAttribute)
# class BooleanAttributeAdmin(AbstractAttributeChildAdmin):
#     base_model = BooleanAttribute
#
#
# @admin.register(TimeAttribute)
# class TimeAttributeAdmin(AbstractAttributeChildAdmin):
#     base_model = TimeAttribute
#
#
# @admin.register(IntegerAttribute)
# class IntegerAttributeAdmin(AbstractAttributeChildAdmin):
#     base_model = IntegerAttribute
#
#
# @admin.register(FloatAttribute)
# class FloatAttributeAdmin(AbstractAttributeChildAdmin):
#     base_model = FloatAttribute
#
#
# @admin.register(TravelAttribute)
# class TravelAttributeAdmin(AbstractAttributeChildAdmin):
#     base_model = TravelAttribute
#
#
# @admin.register(StringAttribute)
# class StringAttributeAdmin(AbstractAttributeChildAdmin):
#     base_model = StringAttribute
#
#
# @admin.register(AbstractAttribute)
# class AbstractAttributeParentAdmin(PolymorphicParentModelAdmin):
#     """ The parent model admin """
#     base_model = AbstractAttribute  # Optional, explicitly set here.
#     child_models = (
#         BooleanAttribute, TimeAttribute, IntegerAttribute, FloatAttribute, TravelAttribute,
#         StringAttribute)
#     list_filter = (PolymorphicChildModelFilter,)  # This is optional.
#     list_display = ('name', 'type', 'template')
