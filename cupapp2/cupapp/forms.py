from datetime import datetime

from django import forms
from django.forms import formset_factory


class NewCup(forms.Form):
    def __init__(self, *args, **kwargs):
        super(NewCup, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

    default_cup_name = "Game-{date}".format(date=datetime.now()).replace(" ", "_")
    name = forms.CharField(max_length=99, initial=default_cup_name, disabled=True)
    description = forms.CharField(max_length=99, strip=True, required=False,
                                  widget=forms.TextInput(attrs={'placeholder': 'Your friendly cup name '}))
    cup_formulas = (
        # ('cup', 'cup'),
        ('league', 'league'),
    )
    form = forms.ChoiceField(choices=cup_formulas)
    modes = (
        ('11', '1 vs 1'),
        ('21', '2 vs 1'),
        ('22', '2 vs 2'),
    )
    mode = forms.ChoiceField(choices=modes)


class Player(forms.Form):
    def __init__(self, *args, **kwargs):
        super(Player, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

    name = forms.CharField(
        max_length=32,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Player Name'
        })
    )
    # stars = forms.IntegerField(max_value=10, min_value=1, initial=8)
    stars_choices = (
        (1, '0.5'), (2, '1'), (3, '1.5'), (4, '2'), (5, '2.5'),
        (6, '3'), (7, '3.5'), (8, '4'), (9, '4.5'), (10, '5'),
    )
    stars = forms.ChoiceField(choices=stars_choices, required=True, initial=10)


PlayerFormset = formset_factory(Player, extra=2)


class SubmitFixture(forms.Form):
    home_goals = forms.IntegerField(min_value=0, max_value=99)
    away_goals = forms.IntegerField(min_value=0, max_value=99)
