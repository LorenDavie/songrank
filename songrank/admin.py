""" 
Admin for Songrank.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from songrank import models


admin.site.register(models.Member, UserAdmin)
admin.site.register(models.Song)
admin.site.register(models.Ranking)
