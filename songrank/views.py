""" 
Views for Songrank.
"""

from songrank.models import Song, Pipeline, Phase, Chopper, Rescue, Chop, ChopperWrapper, SongChop
from songrank.forms import ReschedulePipelineForm
from songrank.calview import MonthView, date_for_offset
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from ics import Calendar, Event
from datetime import date

@login_required(login_url='/admin/login/')
def home(request):
    """ 
    Home page.
    """
    request.user.ensure_rankings()
    aggregate = Song.objects.average_rankings()
    has_chop = Song.objects.has_song_chop(request.user)
    return render(request, "home.html", context={'aggregate':aggregate, 'has_chop':has_chop})

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

def pipeline_calendar(request):
    """ 
    Gets the calendar for the pipelines.
    """
    cal = Calendar()
    for phase in Phase.objects.filter(pipeline__done=False):
        event = Event()
        event.name = f"{phase.pipeline}: {phase.descriptor.name}"
        event.begin = phase.due
        event.make_all_day()
        cal.events.add(event)
    
    response = HttpResponse(cal, content_type="text/calendar")
    return response

@login_required(login_url="/admin/login/")
def calendar(request, month_offset=0, shift=None):
    """ 
    Shows a calendar view of the pipelines.
    """
    offset = int(month_offset)
    if shift == "next":
        offset += 1
    elif shift == "previous":
        offset -= 1
    
    cals = []
    for i in range(6):
        ask_date = date_for_offset(offset+i)
        cal = MonthView(ask_date.year, ask_date.month)
        cals.append(cal)
    
    return render(request, "calendar.html", context={"cals":cals, "offset":offset})

@login_required(login_url="/admin/login/")
def choppers(request):
    """ 
    Shows the songs on the chopping block.
    """
    choppers = [ChopperWrapper(chopper, request.user) for chopper in Chopper.objects.all()]
    return render(request, "choppers.html", context={"choppers":choppers})

@login_required(login_url="/admin/login/")
def chopper_lyrics(request, chopper_id):
    """ 
    Displays the lyrics of the specified chopper.
    """
    chopper = Chopper.objects.get(pk=chopper_id)
    return render(request, "lyrics.html", context={"song":chopper})

@login_required(login_url="/admin/login/")
def rescue_chopper(request, chopper_id):
    """ 
    Rescues the chopper.
    """
    chopper = Chopper.objects.get(pk=chopper_id)
    Rescue.objects.create(member=request.user, chopper=chopper, date=date.today())
    
    # if there is a matching chop then delete it
    try:
        Chop.objects.get(chopper=chopper, member=request.user).delete()
    except Chop.DoesNotExist:
        pass
    
    # should this become a real song again?
    chopper.evaluate_rescues()
    
    return HttpResponseRedirect("/choppers/")

@login_required(login_url="/admin/login/")
def chop_chopper(request, chopper_id):
    """ 
    Chops the chopper.
    """
    chopper = Chopper.objects.get(pk=chopper_id)
    Chop.objects.create(member=request.user, chopper=chopper, date=date.today())
    
    # if there is a matching rescue then delete it
    try:
        Rescue.objects.get(chopper=chopper, member=request.user).delete()
    except Rescue.DoesNotExist:
        pass
    
    # is it time for the chopper to go?
    chopper.evaluate_choppage()
    
    return HttpResponseRedirect("/choppers/")

@login_required(login_url="/admin/login/")
def chopperize(request, song_id):
    """ 
    Chopperizes the song.
    """
    song = Song.objects.get(pk=song_id)
    
    SongChop.objects.create(user=request.user, song=song)
    song.check_chopperize()
    
    return HttpResponseRedirect("/")

@login_required(login_url="/admin/login/")
def unlock_rankings(request):
    """ 
    Unlocks rankings for user.
    """
    user = request.user
    user.rankings_locked = False
    user.save()
    return HttpResponseRedirect("/")

@login_required(login_url="/admin/login/")
def lock_rankings(request):
    """ 
    Unlocks rankings for user.
    """
    user = request.user
    user.rankings_locked = True
    user.save()
    return HttpResponseRedirect("/")
