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
    path("calendar/", views.calendar),
    path("calendar/<str:month_offset>/<str:shift>/", views.calendar),
    path("choppers/", views.choppers),
    path("choppers/<int:chopper_id>/lyrics/", views.chopper_lyrics),
    path("choppers/<int:chopper_id>/rescue/", views.rescue_chopper),
    path("choppers/<int:chopper_id>/chop/", views.chop_chopper),
    path("choppers/chopperize/<int:song_id>/", views.chopperize),
    path("unlock-rankings/", views.unlock_rankings),
    path("lock-rankings/", views.lock_rankings),
    path("add-song-comment/<int:song_id>/", views.add_song_comment),
    path("add-chopper-comment/<int:chopper_id>/", views.add_chopper_comment),
    path('admin/', admin.site.urls),
]
