from django import forms

class ParagraphSearchForm(forms.Form):
    query = forms.CharField(max_length=255, required=True)
    ORDER = [
        ('accuracy', 'Dokładność'),
        ('chrono', 'Data'),
    ]
    order = forms.ChoiceField(
        widget=forms.Select,
        choices=ORDER,
        initial='accuracy',
        required=False
    )
    CHOICES = [
        ('simple', 'Proste wyszukiwanie'),
        ('smart', 'Inteligentne wyszukiwanie'),
        #('hybrid', 'Wyszukiwanie hybrydowe'),
    ]
    search_type = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=CHOICES,
        initial='simple',
        required=True,
    )
