import datetime
import os
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.contrib.auth.models import User
from cities_light.models import SubRegion, Region
from ckeditor.fields import RichTextField

from django.utils.crypto import get_random_string
def user_directory_path(instance, filename):
    # Dosya adını kullanıcı adı ile değiştir
    ext = filename.split('.')[-1]
    filename = f'{instance.username}_{timezone.now().strftime("%Y-%m-%d-%H-%M-%S")}.{ext}'

    # Dosyanın kaydedileceği klasörü belirle
    folder = f'profile_pics/{instance.username}'

    # Klasörü oluştur
    os.makedirs(folder, exist_ok=True)

    # Tam dosya yolu
    return os.path.join(folder, filename)

class Mekan(models.Model):
    adi = models.CharField('Mekan Adı', max_length=20)
    adres = models.CharField(max_length=300)
    telefon_numarasi = models.CharField('Telefon', max_length=11)
    webadresi = models.URLField('Website Adresi')
    email = models.EmailField('Email Adresi')
    sehir = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, blank=True, related_name='sehir')
    ilce = models.ForeignKey(SubRegion, on_delete=models.SET_NULL, null=True, blank=True)
    aciklama = models.TextField('Mekan Açıklaması', null=True, blank=True)
    onayli = models.BooleanField('Onaylı', default=False)
    onay_tarihi = models.DateTimeField('Onay Tarihi', null=True, blank=True)
    def save(self, *args, **kwargs):
        if self.onayli and not self.onay_tarihi:
            self.onay_tarihi = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.adi

# class Profile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     ad = models.CharField(max_length=20)
#     soyad = models.CharField(max_length=20)
#     activity_count = models.IntegerField(default=0)
#     profile_img = models.ImageField(upload_to=user_directory_path)
#     email = models.EmailField(null=True, blank=True)
#     telefon = models.CharField(max_length=11, blank=True, null=True)
#     kayit_tarihi = models.DateTimeField(auto_now_add=True)
#     katildigi_etkinlikler = models.ManyToManyField(Event, related_name='katilimcilar', blank=True)
#     @property
#     def username(self):
#         return self.user.username

#     def __str__(self):
#         return self.ad

#     def update_username(self, new_username, new_password):
#         self.user.username = new_username
#         self.user.set_password(new_password)
#         self.user.save()
class Event(models.Model):
    ad = models.CharField('Etkinlik Adı', max_length=120)
    baslik = models.CharField('Baslik', max_length=50, null=True, blank=True)
    slug = models.SlugField(unique=True, max_length=100, null=True, blank=True)
    saat = models.TimeField('Saat', null=False, blank=False)
    gün = models.DateTimeField('Etkinlik Günü')
    katilimcilar = models.ManyToManyField(User, related_name='katildigi_etkinlikler', blank=True)
    # katilimci_sayisi = models.PositiveIntegerField(default=0)
    mekan = models.ForeignKey(Mekan, blank=True, null=True,related_name='etkinlikler', on_delete=models.CASCADE)
    # Diğer alanlar...
    açiklama = RichTextField()
    yönetici = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name='yönetici_event_set')
    silindi = models.BooleanField(default=False)
    
    def get_katilimcilar(self):
        return self.katilimcilar.all()
    def __str__(self):
        return f"{self.ad} ({self.gün.strftime('%d.%m.%Y %H:%M')})"

    def save(self, *args, **kwargs):
        if not self.baslik:  # Başlık boşsa (yeni etkinlik)
            self.baslik = slugify(self.ad)  # Etkinlik adından başlığı oluştur
        if not self.slug:  # Slug boşsa (yeni etkinlik)
            slug = slugify(self.baslik)
            random_string = get_random_string(length=4)  # Rastgele bir dize oluştur
            self.slug = f"{slug}-{random_string}"  # Slug'a rastgele dizeyi ekle
        super(Event, self).save(*args, **kwargs)
    
    def günü_gecmis(self):
        now = datetime.now()
        event_datetime = datetime.combine(self.gün, self.saat)
        return event_datetime < now
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ad = models.CharField(max_length=20)
    soyad = models.CharField(max_length=20)
    profile_img = models.ImageField(upload_to=user_directory_path)
    email = models.EmailField(null=True, blank=True)
    telefon = models.CharField(max_length=11, blank=True, null=True)
    kayit_tarihi = models.DateTimeField(auto_now_add=True)
    katildigi_etkinlikler = models.ManyToManyField(Event, related_name='katilimcilar_profil', blank=True)
    olusturdugu_etkinlikler = models.ManyToManyField(Event, related_name='olusturan_profil', blank=True)
    @property
    def username(self):
        return self.user.username

    def __str__(self):
        return self.ad

    def update_username(self, new_username, new_password):
        self.user.username = new_username
        self.user.set_password(new_password)
        self.user.save()  

    def get_katildigi_etkinlik_sayisi(self):
        return self.katildigi_etkinlikler.count()