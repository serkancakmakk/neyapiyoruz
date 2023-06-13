from django.contrib import admin

from .models import Event, Profile, Mekan,Yorum,YorumCevap

# # Register your models here.
class MekanAdmin(admin.ModelAdmin):
    list_display=('adi','adres','telefon_numarasi','sehir','ilce','webadresi','email','onayli','acik','onay_tarihi')
    ordering = ('adi',)
    search_fields = ('adi','adres',)
admin.site.register(Mekan, MekanAdmin)
class YorumAdmin(admin.ModelAdmin):
    list_display = ('yorum', 'event_ad', 'yorum_sahibi')
    ordering = ('yorum',)
    search_fields = ('yorum', 'event__ad')

    def event_ad(self, obj):
        return obj.event.ad

    event_ad.short_description = 'Event Adı'
    event_ad.admin_order_field = 'event__ad'

admin.site.register(Yorum, YorumAdmin)
class YorumCevapAdmin(admin.ModelAdmin):
    list_display = ('cevap', 'cevapsahibi', 'silindi')

admin.site.register(YorumCevap, YorumCevapAdmin)


class EventAdmin(admin.ModelAdmin):
    list_display = ('ad', 'gün', 'saat', 'mekan', 'display_katilimcilar', 'display_yorumlar','kontenjan','katilimci_kontrol')

    def display_katilimcilar(self, obj):
        return ", ".join([str(katilimci) for katilimci in obj.katilimcilar.all()])
    display_katilimcilar.short_description = 'Katılımcılar'

    def display_yorumlar(self, obj):
        return ", ".join([str(yorum) for yorum in obj.yorumlar.all()])
    display_yorumlar.short_description = 'Yorumlar'

admin.site.register(Event, EventAdmin)


class ProfileAdmin(admin.ModelAdmin):
    list_display=('user','get_username','ad','soyad','telefon','kayit_tarihi')
    ordering = ('ad',)
    search_fields = ('ad','telefon')
    
    def get_username(self, obj):
        return obj.user.username

    get_username.short_description = 'Username'

admin.site.register(Profile, ProfileAdmin)
