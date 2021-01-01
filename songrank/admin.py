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
admin.site.register(models.Pipeline)
admin.site.register(models.Phase)
