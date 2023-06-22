from django.contrib.auth.models import User
from .models import Bildirim

def bildirimler(request):
    if request.user.is_authenticated:
        bildirimler = Bildirim.objects.filter(bildirim_alani=request.user.profile).order_by('-olusturulma_tarihi')
    else:
        bildirimler = None
    return {'bildirimler': bildirimler}