from django.db import models
from django.utils.translation import gettext_lazy as _


class DescriptionType(models.TextChoices):
    FAQ = 'FAQ', _('FAQ')
    Privacy = 'P', _('Datenschutz')


class StateChoices(models.TextChoices):
    BW = 'BW', _('Baden-Württemberg')
    BY = 'BY', _('Bayern')
    BE = 'BE', _('Berlin')
    BB = 'BB', _('Brandenburg')
    HB = 'HB', _('Bremen')
    HH = 'HH', _('Hamburg')
    HE = 'HE', _('Hessen')
    MV = 'MV', _('Mecklenburg-Vorpommern')
    NI = 'NI', _('Niedersachsen')
    NW = 'NW', _('Nordrhein-Westfalen')
    RP = 'RP', _('Rheinland-Pfalz')
    SL = 'SL', _('Saarland')
    SN = 'SN', _('Sachsen')
    ST = 'ST', _('Sachsen-Anhalt')
    SH = 'SH', _('Schleswig-Holstein')
    TH = 'TH', _('Thüringen')


class ScoutOrganisationLevelChoices(models.TextChoices):
    VERBAND = 'Verband', _('Verband')
    BUND = 'Bund', _('Bund')
    RING = 'Ring', _('Ring/Regional')
    STAMM = 'Stamm', _('Stamm')
    GRUPPE = 'Gruppe', _('Gruppe')
    SCOUT = 'Scout', _('Pfadfinder*innen')

    @staticmethod
    def get_level_choice_plural(choice: str) -> str:
        plural_dict = {
            'Verband': 'Verbände',
            'Bund': 'Bünde',
            'Ringe': 'Ringe',
            'Stamm': 'Stämme',
            'Gruppe': 'Gruppe',
            'Scout': 'Pfadfinder*innen'
        }
        if choice in plural_dict:
            return plural_dict[choice]
        else:
            raise KeyError('Choice does not exist')
