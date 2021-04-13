""" 
Models for songrank.
"""
from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import timedelta, date


class Member(AbstractUser):
    """ 
    A member of the band.
    """
    rankings_locked = models.BooleanField(default=False)
        
    def ensure_rankings(self):
        """ 
        Makes sure there is a default ranking at least for every non-accepted song.
        """
        for song in Song.objects.filter(accepted=False):
            ranking, created = Ranking.objects.get_or_create(member=self, song=song)
    
    def active_rankings(self):
        """ 
        Gets rankings for this user for non-accepted songs.
        """
        return self.rankings.filter(song__accepted=False)
    
    def rebalance_rankings(self):
        """ 
        Rebalances ranking scores after songs are accepted.
        """
        self.ensure_rankings()
        rankings = self.active_rankings()
        score = rankings.count()
        for ranking in rankings:
            ranking.ranking = score
            ranking.save()
            score -= 1
    
    @property
    def initials(self):
        if self.first_name and self.last_name:
            return f"{self.first_name[0]}{self.last_name[0]}"
        else:
            return "??"
            
class SongManager(models.Manager):
    """ 
    Manager for songs.
    """
    def aggregate_rankings(self):
        """ 
        Gets the non-accepted songs by aggregate rank.
        """
        songs = [song for song in self.filter(accepted=False)]
        songs.sort(key=lambda song: song.aggregate_rank(), reverse=True)
        return songs
    
    def average_rankings(self):
        """ 
        Gets non-accepted songs by average rank.
        """
        songs = [song for song in self.filter(accepted=False)]
        songs.sort(key=lambda song: song.average_rank(), reverse=True)
        return songs
    
    def has_song_chop(self, member):
        """ 
        Checks if the member has a song chop for the bottom ranked song.
        """
        if self.all().count() == 0:
            return False # there are no songs, so by definition...
        
        last_song = self.average_rankings()[-1]
        return SongChop.objects.filter(user=member, song=last_song).exists()

class Song(models.Model):
    """ 
    A song.
    """
    writers = models.ManyToManyField(Member, related_name="songs_written")
    name = models.CharField(unique=True, max_length=100)
    demo = models.URLField(null=True, blank=True)
    lyrics = models.TextField(blank=True)
    accepted = models.BooleanField(default=False)
    scheduled_release = models.DateField(null=True, blank=True)
    
    objects = SongManager()

    def __str__(self):
        return self.name
    
    def aggregate_rank(self):
        """ 
        Gets the total rank value for this song.
        """
        return self.rankings.aggregate(models.Sum("ranking"))["ranking__sum"]
    
    def average_rank(self):
        """ 
        Gets the average ranking for the song.
        """
        if not self.rankings.all().exists():
            # avoid divide by zero
            return 0
        
        agg_rank = self.aggregate_rank()
        return agg_rank / self.rankings.count()
    
    def spread(self):
        """ 
        Shows the difference between the top and bottom ranking for this song.
        """
        top_rank = self.rankings.aggregate(models.Max("ranking"))["ranking__max"]
        bottom_rank = self.rankings.aggregate(models.Min("ranking"))["ranking__min"]
        difference = top_rank - bottom_rank
        
        max_spread = Song.objects.filter(accepted=False).count() - 1
        
        if max_spread > 0:
            return float(difference) / float(max_spread)
        else:
            return 0.0
    
    def spread_percent(self):
        """ 
        Gets spread as a percentage.
        """
        spr = self.spread() * 100.0
        return f"{spr:.0f}"
    
    def ranking_incomplete(self):
        """ 
        Returns true if less than all members have ranked the song.
        """
        return self.rankings.all().count() < Member.objects.all().count()
    
    def endorsement(self):
        """ 
        The relative level of endoresement for the song.
        """
        max_endorsement = Song.objects.filter(accepted=False).count()
        return self.average_rank() / float(max_endorsement)
    
    def endorsement_percent(self):
        """ 
        Relative endorsement as a percentage.
        """
        endorsement = self.endorsement() * 100.0
        return f"{endorsement:.0f}"
    
    def check_chopperize(self):
        """ 
        Checks if this song should be chopperized.
        """
        if self.chops.all().count() >= 2:
            # past threshold, chop it
            chopper = Chopper.objects.create(
                name=self.name,
                demo=self.demo,
                lyrics=self.lyrics
            )
            for writer in self.writers.all():
                chopper.writers.add(writer)
            chopper.save()
            self.delete()


class Ranking(models.Model):
    """ 
    A member's ranking of a song.
    """
    member = models.ForeignKey(Member, related_name="rankings", on_delete=models.CASCADE)
    ranking = models.IntegerField(default=0)
    song = models.ForeignKey(Song, related_name="rankings", on_delete=models.CASCADE)
    comments = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.member} : {self.song} : {self.ranking}"
    
    class Meta:
        unique_together = (("member", "song"),)
        ordering = ["-ranking"]

class SongChop(models.Model):
    """ 
    A vote to chop a song and turn it into a chopper.
    """
    song = models.ForeignKey(Song, related_name="chops", on_delete=models.CASCADE)
    user = models.ForeignKey(Member, related_name="song_chops", on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.user} wants to turn {self.song} into a chopper"
    
    class Meta:
        unique_together = (("song", "user"),)


# =============
# = Pipelines =
# =============
class PipelineTemplate(models.Model):
    """ 
    A template for a pipeline.
    """
    name = models.CharField(unique=True, max_length=100)
    
    def __str__(self):
        return self.name

class PhaseDescriptor(models.Model):
    """ 
    A descriptor for a phase in a pipeline.
    """
    template = models.ForeignKey(PipelineTemplate, related_name="phase_descriptors", on_delete=models.CASCADE)
    name = models.CharField(blank=True, max_length=100)
    order = models.IntegerField()
    depends_on = models.ForeignKey("self", null=True, blank=True, related_name="downstream_phase_descriptors", on_delete=models.SET_NULL)
    buffer_days = models.IntegerField(default=1)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ["order"]
        unique_together = (("template", "name"),("template", "order"))

class Pipeline(models.Model):
    """ 
    A release pipeline.
    """
    template = models.ForeignKey(PipelineTemplate, related_name="pipelines", on_delete=models.CASCADE)
    song = models.ForeignKey(Song, null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField(null=True, blank=True, max_length=100)
    done = models.BooleanField(default=False)
    baseline = models.DateField() # actually the release date - work backwards from here
    
    def __str__(self):
        if self.song and self.name:
            return f"{self.song} ({self.name})"
        elif self.song:
            return str(self.song)
        else:
            return self.name
    
    def save(self, *args, **kwargs):
        """ 
        Automatically populate phases if they don't yet exist.
        """
        value = super().save(*args, **kwargs)
        
        if not self.phases.all().exists():
            self.schedule()
        
        return value
    
    def schedule(self):
        """ 
        Sets phase schedles accordingly.
        """
        self.phases.all().delete()
        subsequent_phase = None
        for descriptor in self.template.phase_descriptors.all().order_by("-order"):
            phase = Phase.objects.create(pipeline=self, descriptor=descriptor)
            if subsequent_phase:
                phase.due = subsequent_phase.due - timedelta(days=subsequent_phase.descriptor.buffer_days)
            else:
                phase.due = self.baseline
            phase.save()
            subsequent_phase = phase
    
    def slip_to(self, new_date):
        """ 
        Moves the pipeline to a new release date, adjusting phase schedules accordingly.
        """
        self.baseline = new_date
        self.save()
        self.schedule()
    
    class Meta:
        unique_together = (("song", "name"),)

class Phase(models.Model):
    """ 
    A phase in a pipeline.
    """
    pipeline = models.ForeignKey(Pipeline, related_name="phases", on_delete=models.CASCADE)
    descriptor = models.ForeignKey(PhaseDescriptor, related_name="phases", on_delete=models.CASCADE)
    due = models.DateField(null=True, blank=True)
    done = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.descriptor} : {self.due} ({self.pipeline})"
    
    def is_late(self):
        """ 
        Indicates if this phase is late.
        """
        if self.done:
            return False
        
        return self.due < date.today()
    
    class Meta:
        unique_together = (("pipeline", "descriptor"),)
        ordering = ["due"]


class ChopperManager(models.Manager):
    """ 
    Manager for choppers.
    """
    def needs_rescue(self, member):
        """ 
        Returns the choppers eligible for rescue by the member.
        """
        return self.exclude(pk__in=[rescue.chopper.pk for rescue in member.rescues.all()]).exclude(pk__in=[chop.chopper.pk for chop in member.chops.all()])

class Chopper(models.Model):
    """ 
    A chopper is a song facing being dropped.  Choppers are destined to
    be either formally dropped by the band, or entered into the pipeline.
    """
    writers = models.ManyToManyField(Member, related_name="choppers")
    name = models.CharField(unique=True, max_length=100)
    demo = models.URLField(null=True, blank=True)
    lyrics = models.TextField(blank=True)
    
    def evaluate_choppage(self):
        """ 
        If everyone has decided to chop the song, delete it.
        """
        if self.chops.all().count() >= Member.objects.count():
            self.delete()
    
    def evaluate_rescues(self):
        """ 
        If half or more members want to rescue the song it becomes a
        real song again.
        """
        threshold = Member.objects.count() / 2
        if self.rescues.all().count() >= threshold:
            song = Song.objects.create(
                name=self.name,
                demo=self.demo,
                lyrics=self.lyrics
            )
            for writer in self.writers.all():
                song.writers.add(writer)
            song.save()
            
            # now we're a real song. get rid of the chopper
            self.delete()
    
    objects = ChopperManager()
    
    def __str__(self):
        return self.name

class ChopperWrapper(object):
    """ 
    Wrapper for a chopper showing a user's POV
    """
    def __init__(self, chopper, member):
        self.chopper = chopper
        self.member = member
    
    def can_chop(self):
        """ 
        Returns true if the user hasn't already chopped the song.
        """
        return not Chop.objects.filter(member=self.member, chopper=self.chopper).exists()
    
    def can_rescue(self):
        """ 
        Returns true if the user hasn't rescued today or if they
        haven't yet rescued this song.
        """
        if self.member.rescues.filter(date=date.today()).exists():
            return False
        
        return not Rescue.objects.filter(member=self.member, chopper=self.chopper).exists()
    
    def __getattr__(self, attr):
        return getattr(self.chopper, attr)


class RescueManager(models.Manager):
    """ 
    Manager for rescues.
    """
    def can_rescue(self, member):
        """ 
        Determines if the member can rescue today.
        """
        return not member.rescues.filter(date=date.today()).exists()

class Rescue(models.Model):
    """ 
    A rescue is a vote to rescue a chopper by a member.
    """
    chopper = models.ForeignKey(Chopper, related_name="rescues", on_delete=models.CASCADE)
    member = models.ForeignKey(Member, related_name="rescues", on_delete=models.CASCADE)
    reason = models.TextField(blank=True)
    date = models.DateField()
    
    objects = RescueManager()
    
    def __str__(self):
        return f"{self.member} wants to rescue {self.chopper}"
    
    class Meta:
        unique_together = (("member", "chopper"),)

class Chop(models.Model):
    """ 
    A vote to chop a song.
    """
    chopper = models.ForeignKey(Chopper, related_name="chops", on_delete=models.CASCADE)
    member = models.ForeignKey(Member, related_name="chops", on_delete=models.CASCADE)
    date = models.DateField()
    
    def __str__(self):
        return f"{self.member} wants to chop {self.chopper}"
    
    class Meta:
        unique_together = (("member", "chopper"),)

