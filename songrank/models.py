""" 
Models for songrank.
"""
from django.db import models
from django.contrib.auth.models import AbstractUser


class Member(AbstractUser):
    """ 
    A member of the band.
    """    
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
        agg_rank = self.aggregate_rank()
        return agg_rank / self.rankings.count()


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

