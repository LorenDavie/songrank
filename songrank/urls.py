"""songrank URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from songrank import views

urlpatterns = [
    path("", views.home),
    path("lyrics/<int:song_id>/", views.lyrics),
    path("rank/", views.rank),
    path("pipelines/", views.pipelines),
    path("pipelines/<int:pipeline_id>/<int:phase_id>/done/", views.complete_phase),
    path("pipelines/<int:pipeline_id>/reschedule/", views.reschedule_pipeline),
    path("pipelines/calendar.ics", views.pipeline_calendar),
    path('admin/', admin.site.urls),
]
