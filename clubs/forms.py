from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profil, Club, Evenement

class InscriptionForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True, label='Prénom')
    last_name = forms.CharField(max_length=50, required=True, label='Nom')
    email = forms.EmailField(required=True, label='Email')
    telephone = forms.CharField(max_length=20, required=False, label='Téléphone')

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'telephone', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            Profil.objects.create(
                user=user,
                telephone=self.cleaned_data.get('telephone', ''),
                role='etudiant'
            )
        return user

class ProfilForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50, label='Prénom')
    last_name = forms.CharField(max_length=50, label='Nom')
    email = forms.EmailField(label='Email')

    class Meta:
        model = Profil
        fields = ['telephone', 'photo', 'bio']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email

class ClubForm(forms.ModelForm):
    class Meta:
        model = Club
        fields = ['nom', 'description', 'categorie', 'logo']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class EvenementForm(forms.ModelForm):
    class Meta:
        model = Evenement
        fields = ['titre', 'description', 'date_debut', 'date_fin', 'lieu', 'capacite_max', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'date_debut': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'date_fin': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
