""" 
Manually kicks off rebalancing the rankings.
"""
from django.core.management.base import BaseCommand, CommandError
from songrank.models import Member


class Command(BaseCommand):
    """ 
    Command class.
    """
    def handle(self, *args, **options):
        """ 
        Rebalances the rankings for each member.
        """
        for member in Member.objects.all():
            member.rebalance_rankings()
