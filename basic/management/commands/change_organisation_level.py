from django.core.management.base import BaseCommand

from basic.choices import ScoutOrganisationLevelChoices
from basic.models import ScoutHierarchy


class Command(BaseCommand):
    help = ''

    def handle(self, *args, **options):
        level_dict = {
            1: ScoutOrganisationLevelChoices.SCOUT,
            2: ScoutOrganisationLevelChoices.VERBAND,
            3: ScoutOrganisationLevelChoices.BUND,
            4: ScoutOrganisationLevelChoices.RING,
            5: ScoutOrganisationLevelChoices.STAMM,
            6: ScoutOrganisationLevelChoices.GRUPPE
        }

        heads = ScoutHierarchy.objects.all()
        for head in heads:
            head.level_choice = level_dict.get(head.level.id, ScoutOrganisationLevelChoices.GRUPPE)
            head.save()

