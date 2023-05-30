from django.contrib import admin

from .models import Event, Profile, Mekan

# # Register your models here.
class MekanAdmin(admin.ModelAdmin):
    list_display=('adi','adres','telefon_numarasi','sehir','ilce','webadresi','email','onayli','onay_tarihi')
    ordering = ('adi',)
    search_fields = ('adi','adres',)

admin.site.register(Mekan, MekanAdmin)

class EventAdmin(admin.ModelAdmin):
    list_display = ('ad', 'gün', 'saat', 'mekan', 'display_katilimcilar')

    def display_katilimcilar(self, obj):
        return ", ".join([str(katilimci) for katilimci in obj.katilimcilar.all()])
    display_katilimcilar.short_description = 'Katılımcılar'
admin.site.register(Event, EventAdmin)

class ProfileAdmin(admin.ModelAdmin):
    list_display=('user','get_username','ad','soyad','telefon','kayit_tarihi')
    ordering = ('ad',)
    search_fields = ('ad','telefon')
    
    def get_username(self, obj):
        return obj.user.username

    get_username.short_description = 'Username'

admin.site.register(Profile, ProfileAdmin)
