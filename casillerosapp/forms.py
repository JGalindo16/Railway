from django import forms
from .models import Casillero
from casillerosapp.choices import KEY_CHOICES

class UsuarioCasilleroForm(forms.Form):
    usuario_email = forms.EmailField(
        required=False,
        label="Email Dueño",
        widget=forms.EmailInput(attrs={
            'placeholder': 'Ingrese email dueño',
            'style': 'width: 65%;'
        })
    )
    
    # Campos de la clave con clase 'form-select' para Select2
    clave1 = forms.ChoiceField(
        choices= KEY_CHOICES,
        label="Clave 1",
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    clave2 = forms.ChoiceField(
        choices=KEY_CHOICES,
        label="Clave 2",
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    clave3 = forms.ChoiceField(
        choices=KEY_CHOICES,
        label="Clave 3",
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    clave4 = forms.ChoiceField(
        choices=KEY_CHOICES,
        label="Clave 4",
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, casillero=None, **kwargs):
        super().__init__(*args, **kwargs)
        if casillero and casillero.email:
            self.fields['usuario_email'].widget.attrs['placeholder'] = casillero.email
            # Si hay una clave ya existente, predefinirla en los selectores
            if casillero.clave:
                clave = casillero.clave
                self.fields['clave1'].initial = clave[0]
                self.fields['clave2'].initial = clave[1]
                self.fields['clave3'].initial = clave[2]
                self.fields['clave4'].initial = clave[3]
