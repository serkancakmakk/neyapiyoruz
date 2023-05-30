
from django import forms
from django.forms import ModelForm, TimeInput, Widget
from django import forms
from django.forms import widgets
from django.forms import ModelForm
from cities_light.models import Region, SubRegion
from .models import Profile, Mekan,Event
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from ckeditor_uploader.fields import RichTextUploadingField
class MekanForm(ModelForm):
    sehir = forms.ModelChoiceField(queryset=Region.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))
    ilce = forms.ModelChoiceField(queryset=SubRegion.objects.none(), widget=forms.Select(attrs={'class': 'form-control'}))
    aciklama = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Açıklama'}))

    class Meta:
        model = Mekan
        fields = ('adi', 'adres', 'sehir', 'ilce', 'aciklama', 'email', 'webadresi', 'telefon_numarasi')
        widgets = {
            'adi': forms.TextInput(attrs={'class': 'form-control'}),
            'adres': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.TextInput(attrs={'class': 'form-control'}),
            'telefon_numarasi': forms.TextInput(attrs={'class': 'form-control'}),
            'webadresi': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            sehir_id = self.instance.sehir.id
            self.fields['ilce'].queryset = SubRegion.objects.filter(region_id=sehir_id).order_by('id')
        if 'sehir' in self.data:
            sehir_id = self.data.get('sehir')
            self.fields['ilce'].queryset = SubRegion.objects.filter(region_id=sehir_id).order_by('name')


class EtkinlikForm(forms.ModelForm):
    sehir = forms.ModelChoiceField(queryset=Region.objects.all(), widget=forms.Select(attrs={'class': 'form-control', 'id': 'sehir-select'}))
    ilce = forms.ModelChoiceField(queryset=SubRegion.objects.none(), widget=forms.Select(attrs={'class': 'form-control', 'id': 'ilce-select'}))
    mekan = forms.ModelChoiceField(queryset=Mekan.objects.none(), widget=forms.Select(attrs={'class': 'form-control', 'id': 'mekan-select'}))
    gün = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    saat = forms.TimeField(widget=TimeInput(attrs={'class': 'form-control', 'type': 'time'}))
    açiklama = RichTextUploadingField(config_name='simple_toolbar_config')

    class Meta:
        model = Event
        fields = ['ad', 'gün', 'mekan', 'saat','sehir', 'ilce', 'açiklama']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            sehir_id = self.instance.sehir.id
            self.fields['ilce'].queryset = SubRegion.objects.filter(region_id=sehir_id).order_by('id')
            self.fields['mekan'].queryset = Mekan.objects.filter(ilce__region_id=sehir_id).order_by('id')
        if 'sehir' in self.data:
            sehir_id = self.data.get('sehir')
            self.fields['ilce'].queryset = SubRegion.objects.filter(region_id=sehir_id).order_by('name')
            self.fields['mekan'].queryset = Mekan.objects.filter(ilce__region_id=sehir_id).order_by('id')


class RegistrationForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
    
from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User
from .models import Profile

from django.contrib.auth.forms import UserChangeForm

from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User

from django import forms
from .models import Profile
from django.contrib.auth.forms import PasswordChangeForm
from django.forms import ClearableFileInput

class ProfileUpdateForm(forms.ModelForm):
    email = forms.EmailField()
    username = forms.CharField()
    profile_img = forms.ImageField(widget=forms.ClearableFileInput(attrs={'multiple': False}), required=False)
    old_password = forms.CharField(widget=forms.PasswordInput, required=False)
    new_password1 = forms.CharField(widget=forms.PasswordInput, required=False)
    new_password2 = forms.CharField(widget=forms.PasswordInput, required=False)

    class Meta:
        model = Profile
        fields = ['ad', 'soyad', 'telefon', 'email', 'username', 'profile_img']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].initial = self.instance.user.email
        self.fields['email'].label = 'E-Posta Adresi'
        self.fields['username'].initial = self.instance.user.username
        self.fields['username'].label = 'Kullanıcı Adı'
        self.fields['old_password'].label = 'Eski Şifre'
        self.fields['new_password1'].label = 'Yeni Şifre'
        self.fields['new_password2'].label = 'Tekrar Şifre'

    def clean(self):
        cleaned_data = super().clean()
        old_password = cleaned_data.get('old_password')
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')

        if old_password and not self.instance.user.check_password(old_password):
            raise forms.ValidationError("Mevcut şifre yanlış.")

        if new_password1 != new_password2:
            raise forms.ValidationError("Yeni şifreler eşleşmiyor.")

        return cleaned_data

    def save(self, commit=True):
        user = self.instance.user
        new_password = self.cleaned_data.get('new_password1')

        if new_password:
            user.set_password(new_password)

        profile = super().save(commit=False)
        profile.user = user

        if commit:
            profile.save()

        # Profil resmi dosyasını kaydetme işlemi
        profile_img = self.cleaned_data.get('profile_img')
        if profile_img:
            profile.profile_img = profile_img
            profile.save()

        return profile
