
from otree.api import *
c = cu

doc = ''
class C(BaseConstants):
    NAME_IN_URL = 'instruction'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
class Subsession(BaseSubsession):
    pass
class Group(BaseGroup):
    pass
class Player(BasePlayer):
    pass

class Instruction(Page):
    form_model = 'player'
    timeout_seconds = 120
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1


page_sequence = [Instruction]