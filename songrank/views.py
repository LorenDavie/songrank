""" 
Views for Songrank.
"""

from songrank.models import Song
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

@login_required(login_url='/admin/login/')
def home(request):
    """ 
    Home page.
    """
    request.user.ensure_rankings()
    aggregate = Song.objects.average_rankings()
    return render(request, "home.html", context={'aggregate':aggregate})

@login_required(login_url='/admin/login/')
def lyrics(request, song_id):
    """ 
    Gets lyrics for a song.
    """
    song = Song.objects.get(pk=song_id)
    return render(request, "lyrics.html", context={"song":song})

@login_required(login_url='/admin/login/')
def rank(request):
    """ 
    Ranks the songs.
    """
    active_rankings = request.user.active_rankings()
    rank_value = active_rankings.count()
    new_user_ranks = [int(rank) for rank in request.GET['ranks'].split(",")]
    print("new rankings in order are:", new_user_ranks)
    for rank_id in new_user_ranks:
        rank = active_rankings.get(pk=rank_id)
        rank.ranking = rank_value
        rank.save()
        print("Added rank value", rank_value, "to song", rank.song)
        rank_value -= 1
    
    return HttpResponse('OK')
