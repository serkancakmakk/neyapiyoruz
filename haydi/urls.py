from django import views
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.static import static
from . import views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
urlpatterns = [
path('', views.home, name='home'),
path('<int:year>/<str:month>/', views.home, name='home'),
path('mekan_ekle/', views.mekanekle, name='mekanekle'),
path('get-ilceler/<int:sehir_id>/', views.get_ilceler, name='get_ilceler'),   
path('eventlist', views.eventlist, name='eventlist'),
path('update_profile', views.update_profile, name='update_profile'),
path('eventdetail/<slug:slug>', views.eventdetail, name='eventdetail'),
path('yer_listesi/', views.yer_listesi, name='yer_listesi'), 
path('yer_detay/<int:pk>', views.yer_detay, name='yer_detay'),
path('arama_sonuclari/', views.arama_sonuclari, name='arama_sonuclari'),
path('etkinlik_ekle', views.etkinlik_ekle, name='etkinlik_ekle'),
path('get-mekanlar/<int:ilce_id>/', views.get_mekanlar, name='get_mekanlar'),
path('register/', views.register, name='register'),
path('login/', views.login_view, name='login'),
path('my_profile/', views.my_profile, name='my_profile'),
path('show_profile/<str:username>/', views.show_profile, name='show_profile'),
path('katilimci_ol/<slug:slug>/', views.katilimci_ol, name='katilimci_ol'),
path('katilmayi_birak/<slug:slug>/', views.katilmayi_birak, name='katilmayi_birak'),
path('etkinlik/<slug:slug>/sil/', views.etkinlik_sil, name='etkinlik_sil'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)