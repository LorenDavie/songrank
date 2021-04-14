""" 
Admin for Songrank.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from songrank import models


admin.site.register(models.Member, UserAdmin)
admin.site.register(models.Song)
admin.site.register(models.Ranking)

admin.site.register(models.PipelineTemplate)
admin.site.register(models.PhaseDescriptor)

class PhaseInline(admin.TabularInline):
    """ 
    Inline for phases
    """
    model = models.Phase

class PipelineAdmin(admin.ModelAdmin):
    """ 
    Admin for pipelines.
    """
    model = models.Pipeline
    inlines = [PhaseInline]

admin.site.register(models.Pipeline, PipelineAdmin)
admin.site.register(models.Chopper)
admin.site.register(models.Chop)
admin.site.register(models.SongChop)
admin.site.register(models.SongComment)
admin.site.register(models.ChopperComment)