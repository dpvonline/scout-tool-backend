from django.contrib import admin

from .models import Tag, TagCategory, Activity, Image, MaterialItem, ExperimentItem, Experiment, MaterialName, MaterialUnit

admin.site.register(Activity)

admin.site.register(TagCategory)
admin.site.register(Tag)

admin.site.register(Image)

admin.site.register(Experiment)
admin.site.register(ExperimentItem)

admin.site.register(MaterialItem)
admin.site.register(MaterialUnit)
admin.site.register(MaterialName)
