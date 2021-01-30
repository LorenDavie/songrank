""" 
Views for Songrank.
"""

from songrank.models import Song, Pipeline
from songrank.forms import ReschedulePipelineForm
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
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

@login_required(login_url="/admin/login/")
def pipelines(request):
    """ 
    Shows release pipelines.
    """
    pipelines = Pipeline.objects.filter(done=False).order_by("baseline")
    return render(request, "pipelines.html", context={"pipelines":pipelines})

@login_required(login_url="/admin/login/")
def complete_phase(request, pipeline_id, phase_id):
    """ 
    Completes the pipelne phase.
    """
    pipeline = Pipeline.objects.get(pk=pipeline_id)
    phase = pipeline.phases.get(pk=phase_id)
    phase.done = True
    phase.save()
    
    # if all phases are done, the pipeline is done
    if not pipeline.phases.filter(done=False).exists():
        pipeline.done = True
        pipeline.save()
    
    return HttpResponseRedirect("/pipelines/")

@login_required(login_url="/admin/login/")
def reschedule_pipeline(request, pipeline_id):
    """ 
    Reschedules the specified pipeline.
    """
    pipeline = Pipeline.objects.get(pk=pipeline_id)
    form = None
    if request.method == 'POST':
        form = ReschedulePipelineForm(request.POST)
        if form.is_valid():
            new_due_date = form.cleaned_data['new_due_date']
            pipeline.slip_to(new_due_date)
            return HttpResponseRedirect('/pipelines/')
    else:
        form = ReschedulePipelineForm()
    
    return render(request, "reschedule_pipeline_form.html", context={"form":form, "pipeline":pipeline})
