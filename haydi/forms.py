
from django import forms
from django.forms import ModelForm, TimeInput, Widget
from django import forms
from django.forms import widgets
from django.forms import ModelForm
from cities_light.models import Region, SubRegion

from .widget import CalendarWidget
from .models import Profile, Mekan,Event, Yorum, YorumCevap
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
        if 'sehir' in self.data and self.data['sehir']:
            sehir_id = self.data['sehir']
            self.fields['ilce'].queryset = SubRegion.objects.filter(region_id=sehir_id).order_by('name')

    def clean(self):
        cleaned_data = super().clean()
        sehir = cleaned_data.get('sehir')
        if sehir:
            ilce_queryset = SubRegion.objects.filter(region_id=sehir.id).order_by('name')
            self.fields['ilce'].queryset = ilce_queryset

        return cleaned_data

class MekanUpdateForm(forms.ModelForm):

    class Meta:
        model = Mekan
        fields = ('adi', 'adres', 'aciklama', 'email', 'webadresi', 'telefon_numarasi')
        widgets = {
            'adi': forms.TextInput(attrs={'class': 'form-control'}),
            'adres': forms.TextInput(attrs={'class': 'form-control'}),
            'aciklama': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Açıklama'}),
            'email': forms.TextInput(attrs={'class': 'form-control'}),
            'webadresi': forms.TextInput(attrs={'class': 'form-control'}),
            'telefon_numarasi': forms.TextInput(attrs={'class': 'form-control'}),
        }




class EtkinlikForm(forms.ModelForm):
    sehir = forms.ModelChoiceField(queryset=Region.objects.all(), widget=forms.Select(attrs={'class': 'form-control', 'id': 'sehir-select'}))
    ilce = forms.ModelChoiceField(queryset=SubRegion.objects.none(), widget=forms.Select(attrs={'class': 'form-control', 'id': 'ilce-select'}))
    mekan = forms.ModelChoiceField(queryset=Mekan.objects.none(), widget=forms.Select(attrs={'class': 'form-control', 'id': 'mekan-select'}))
    gün = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    kontenjan = forms.IntegerField(label='Kontenjan', required=False)
    katilimci_kontrol = forms.BooleanField(label='Katılımcı Kontrolü', required=False)
    saat = forms.TimeField(widget=TimeInput(attrs={'class': 'form-control', 'type': 'time'}))
    açiklama = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Event
        fields = ['ad', 'gün', 'mekan', 'saat','sehir', 'ilce', 'açiklama','kontenjan','katilimci_kontrol']

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

class EtkinlikUpdateForm(forms.ModelForm):
    saat = forms.TimeField(widget=TimeInput(attrs={'class': 'form-control', 'type': 'time'}))
    açiklama = RichTextUploadingField(config_name='simple_toolbar_config')
    kontenjan = forms.IntegerField(required=False,min_value=0, initial=0, widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Kaç kişi katılabilir?'}))

    class Meta:
        model = Event
        fields = ['gün', 'mekan', 'saat', 'açiklama','katilimci_kontrol','kontenjan']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'mekan' in self.fields:
            self.fields['mekan'].widget.attrs['class'] = 'form-control'
            self.fields['mekan'].queryset = Mekan.objects.filter(sehir_id=self.instance.mekan.sehir_id).order_by('id')
        if 'gün' in self.fields:
            self.fields['gün'].widget.attrs['class'] = 'form-control'
            self.fields['gün'].widget.attrs['type'] = 'date'

        if self.instance.katilimci_kontrol:
            self.initial['katilimci_kontrol'] = True
        else:
            self.initial['katilimci_kontrol'] = False

    def clean_katilimci_sayisi(self):
        katilimci_kontrol = self.cleaned_data.get('katilimci_kontrol')
        kontenjan = self.cleaned_data.get('kontenjan')

    def clean(self):
        cleaned_data = super().clean()
        
        return cleaned_data

# def clean(self):
#     cleaned_data = super().clean()
#     katilimci_kontrol = cleaned_data.get('katilimci_kontrol')
#     katilimci_sayisi = cleaned_data.get('katilimci_sayisi', 0)

#     if not katilimci_kontrol:
#         katilimci_sayisi = 0

#     if katilimci_sayisi < 0:
#         raise forms.ValidationError("Negatif bir katılımcı sayısı giremezsiniz.")

#     mevcut_katilimci_sayisi = Event.katilimcilar.all().count

#     if katilimci_sayisi < mevcut_katilimci_sayisi:
#         raise forms.ValidationError("Yeni katılımcı sayısı mevcut katılımcı sayısından az olamaz.")

#     cleaned_data['katilimci_sayisi'] = katilimci_sayisi
#     return cleaned_data


class YorumForm(forms.ModelForm):
    class Meta:
        model = Yorum
        fields = ('yorum',)
        widgets = {
            'yorum': forms.TextInput(attrs={'class': 'form-control'}),
        }
class CevapForm(forms.ModelForm):
    class Meta:
        model = YorumCevap
        fields = ('cevap',)
        widgets = {
            'cevap': forms.TextInput(attrs={'class': 'form-control'}),
        }






class RegistrationForm(UserCreationForm):
    email = forms.EmailField()

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email')

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        # Parola doğrulama işlemlerini burada gerçekleştirin
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Parolalar eşleşmiyor.")
        
        # Diğer parola doğrulama kurallarını burada kontrol edin
        # Örneğin, parolanın en az 8 karakter içermesi gerektiğini kontrol edebilirsiniz

        return password2

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Bu e-posta zaten kullanılıyor.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user



    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

from django.contrib.auth.forms import UserChangeForm

from django.contrib.auth.forms import PasswordChangeForm

class ProfileUpdateForm(forms.ModelForm):
    email = forms.EmailField()
    username = forms.CharField()
    profile_img = forms.ImageField(widget=forms.ClearableFileInput(attrs={'multiple': False, 'clearable': True}), required=False)
    clear_profile_img = forms.BooleanField(required=False, initial=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    new_password1 = forms.CharField(widget=forms.PasswordInput, required=False)
    new_password2 = forms.CharField(widget=forms.PasswordInput, required=False)

    class Meta:
        model = Profile
        fields = ['ad', 'soyad', 'telefon', 'email', 'username', 'profile_img']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial['email'] = self.instance.user.email
        self.fields['email'].label = 'E-Posta Adresi'
        self.initial['username'] = self.instance.user.username
        self.fields['username'].label = 'Kullanıcı Adı'
        self.fields['new_password1'].label = 'Yeni Şifre'
        self.fields['new_password2'].label = 'Tekrar Şifre'

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')
        cleaned_data = super().clean()
        clear_profile_img = cleaned_data.get('clear_profile_img')

        if clear_profile_img:
         cleaned_data['profile_img'] = None

        if new_password1 and not new_password2:
            raise forms.ValidationError("Lütfen yeni şifreyi tekrar girin.")

        if new_password1 != new_password2:
            raise forms.ValidationError("Yeni şifreler eşleşmiyor.")

        return cleaned_data

    def save(self, commit=True):
        user = self.instance.user
        new_password = self.cleaned_data.get('new_password1')

        if new_password:
            user.set_password(new_password)
            user.save()

        profile = super().save(commit=False)
        profile.user = user

        if commit:
            profile.save()

        # Profil resmi dosyasını kaydetme işlemi
        profile_img = self.cleaned_data.get('profile_img')
        if profile_img:
            profile.profile_img = profile_img

        # Profil resmini temizleme işlemi
        if self.cleaned_data.get('clear_profile_img'):
            profile.profile_img = None

        profile.save()

        return profile
from django import forms

class MyForm(forms.Form):
   date = forms.DateField(widget=forms.TextInput(attrs={'class': 'datepicker'}))

