
import time
from django.shortcuts import redirect, render
import locale
import calendar
from .forms import CevapForm, EtkinlikUpdateForm, MekanUpdateForm, ProfileUpdateForm, RegistrationForm, YorumForm
from django.contrib.auth.models import User
from django.contrib.auth import logout
from calendar import HTMLCalendar
from datetime import date, datetime,timedelta
from django.urls import reverse
from .forms import EtkinlikForm, MekanForm
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from cities_light.models import City,Region,SubRegion
from django.template.loader import render_to_string
from .models import Bildirim, Mekan,Event, Profile, Yorum, YorumCevap
from .forms import MekanForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.core.paginator import Paginator, Page

from django.contrib.auth.decorators import login_required
# def navbar(request):
#     bildirimler = Bildirim.objects.filter(bildirim_alani=request.user.profile).order_by('-bildirim.olusturulma_tarihi')
#     user = request.user
#     context = {
#         'bildirimler': bildirimler,
#         'user': user,
#     }
#     return render(request, 'navbar.html', context)
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def bildirim_acildi(request):
    user = request.user
    profile = user.profile
    if request.method == "POST":
        if profile.bildirim_sayisi == 0:
            print('Buraya geldi')
            return HttpResponse(status=200)  # İs
        else:
            print('Buraya geldi else kısmı')
            profile.bildirim_sayisi = 0
            profile.save()
            return HttpResponse(status=200)  # İs

def get_ilceler(request, sehir_id):
    ilceler = SubRegion.objects.filter(region_id=sehir_id).values('id', 'name')
    return JsonResponse(list(ilceler), safe=False)
# Create your views here.
@login_required 
def mekanekle(request, year=None, month=None):
    if year is None:
        year = datetime.now().year
    if month is None:
        month = datetime.now().strftime('%B')
    
    submitted = False
    
    if request.method == "POST":
        form = MekanForm(request.POST)
        if form.is_valid():
            mekan = form.save(commit=False)
            if request.user.is_authenticated:
                mekan.olusturan = request.user
            mekan.save()
            submitted = True
            return HttpResponseRedirect(reverse('mekanekle') + '?submitted=True')
    else:
        form = MekanForm()
    
    if 'submitted' in request.GET:
        submitted = True
    
    data = create_calendar(year, month)
    return render(request, 'yer_ekle.html', {'form': form, **data, 'submitted': submitted})


    
def create_calendar(year, month):#iki viewsda da aynısnı yapmamak için ayrı bir fonksiyon tanımladım
    # Türkçe ay adını ayarlama
    locale.setlocale(locale.LC_ALL, 'tr_TR.UTF-8')
    month = month.capitalize()
    # Ayları isimden sayıya dönüştür
    month_number = list(calendar.month_name).index(month)
    month_number = int(month_number)

    # Takvimi oluştur
    cal = calendar.HTMLCalendar().formatmonth(year, month_number)

    # Şimdiki yılı ve saati getir
    now = datetime.now()
    current_year = now.year
    time = now.strftime('%I:%M:%S')
    day = now.day

    # Bir sonraki ayın adını ve yılını hesapla
    if month_number == 12:
        next_month_number = 1
        next_year = year + 1
    else:
        next_month_number = month_number + 1
        next_year = year

    current_month = calendar.month_name[now.month]
    next_month = calendar.month_name[next_month_number]

    return {

        "year": year,
        "day": day,
        "month": month,
        "current_month": current_month,
        "month_number": month_number,
        "cal": cal,
        "now": now,
        "current_year": current_year,
        "time": time,
        "next_month": next_month.lower(),
        "next_year": next_year,
    }

def yer_listesi(request,year=None, month=None):
    if year is None:
        year = datetime.now().year
    if month is None:
        month = datetime.now().strftime('%B')
    mekan = Mekan.objects.filter(onayli=True)
    data = create_calendar(year, month)

    return render(request, 'yer_listesi.html',{'mekan':mekan , **data})
def yer_detay(request, pk, year=None, month=None):
    if year is None:
        year = datetime.now().year
    if month is None:
        month = datetime.now().strftime('%B')
    begeni_durumu = request.session.get('begeni_durumu', 'none')
    mekan = get_object_or_404(Mekan, pk=pk)
    user = request.user
    olumlu_oy_durumu = mekan.olumlu_oy_kullananlar.filter(id=user.id).exists()
    olumsuz_oy_durumu = mekan.olumsuz_oy_kullananlar.filter(id=user.id).exists()

    
    etkinlikler = mekan.etkinlikler.exclude(silindi=True)
    oy_sayisi = mekan.olumlu_oy + mekan.olumsuz_oy
    if oy_sayisi > 0:
        rating = (mekan.olumlu_oy / oy_sayisi) * 5  # Yıldız sayısını hesaplama
    else:
        rating = 0
    data = create_calendar(year, month)
    return render(request, 'etkinlik/yer_detay.html', {'mekan': mekan,'begeni_durumu':begeni_durumu,'rating': rating,'olumsuz_oy_durumu': olumsuz_oy_durumu, 'olumlu_oy_durumu': olumlu_oy_durumu, 'etkinlikler': etkinlikler, **data})

def eventlist(request,year=None, month=None):
    if year is None:
        year = datetime.now().year
    if month is None:
        month = datetime.now().strftime('%B')
    events = Event.objects.all()

    data = create_calendar(year, month)

    return render(request, 'event_list.html',{'events':events,**data} )

def eventdetail(request, slug, year=None, month=None):
    if year is None:
        year = datetime.now().year
    if month is None:
        user = request.user
        form = YorumForm()
        cevapform = CevapForm()
        cevaplar_listesi = YorumCevap.objects.select_related('cevapsahibi').filter(yorum__event__slug=slug)
        profile = request.user.profile
        month = datetime.now().strftime('%B')
        data = create_calendar(year, month)
        etkinlik = get_object_or_404(Event, slug=slug)
        yorumlar = etkinlik.yorumlar.filter(silindi=False).order_by('-id')
        sayfa_sayisi = 4  # Her sayfada gösterilecek yorum sayısı
        paginatör = Paginator(yorumlar, sayfa_sayisi)
        sayfa_numarasi = request.GET.get('sayfa')  # URL parametresinden sayfa numarasını alın
        sayfa = paginatör.get_page(sayfa_numarasi)
        katilimcilar = etkinlik.katilimcilar.all()
        son_yorumlar = yorumlar.order_by('-id')[:2]

        if user.is_authenticated:
            if etkinlik.silindi:
                return render(request, 'etkinlik/etkinlik_silindi.html', {'etkinlik': etkinlik, **data})
            else:
                return render(request, 'etkinlik/eventdetail.html', {'etkinlik': etkinlik, 'katilimcilar': katilimcilar,
                                                                     'profile': profile, 'form': form,
                                                                     'yorumlar': sayfa, 'sayfa': sayfa, **data,
                                                                     'son_yorumlar': son_yorumlar,
                                                                     'cevapform': cevapform,
                                                                     'cevaplar_listesi': cevaplar_listesi})
        else:
            return redirect('login')



    
def home(request, year=None, month=None):
    # Varsayılan olarak geçerli yıl ve ayı ata
    if year is None:
        year = datetime.now().year
    if month is None:
        month = datetime.now().strftime('%B')
    bildirimler = Bildirim.objects.filter(bildirim_alani=request.user.profile).order_by('-id')
    data = create_calendar(year, month)

    # Şehirleri sorgula ve context'e ekle
    sehirler = Region.objects.all()[:10]
    data["sehirler"] = sehirler
    data["bildirimler"] = bildirimler

    return render(request, 'home.html', data)



from django.db.models import Q
def arama_sonuclari(request, year=None, month=None):
    if year is None:
        year = datetime.now().year
    if month is None:
        month = datetime.now().strftime('%B')

    data = create_calendar(year, month)
        
    if request.method == "POST":
        searched = request.POST['searched']
        
        # Mekanları ara
        yerler = Mekan.objects.filter(
            # Şehir veya ilçe alanında tam eşleşmeleri ara (büyük/küçük harf duyarlılığı olmadan)
            Q(sehir__name__iexact=searched) | Q(ilce__name__iexact=searched)
        )
        
        # Etkinlikleri ara
        etkinlikler = Event.objects.filter(
            # Mekan veya ad alanında kısmi eşleşmeleri ara (büyük/küçük harf duyarlılığı olmadan)
            Q(mekan__adi__icontains=searched) | Q(ad__icontains=searched)
        )
        
        return render(request, 'arama_sonuclari.html', {'searched': searched, 'yerler': yerler, 'etkinlikler': etkinlikler, **data})
    else:
        return render(request, 'arama_sonuclari.html', {**data})
def etkinlik_sil(request, slug):
    etkinlik = get_object_or_404(Event, slug=slug)
    katilimcilar = etkinlik.katilimcilar.all()
    now = datetime.now()
    event_datetime = datetime.combine(etkinlik.gün, etkinlik.saat)
    if request.method == "POST":
        if event_datetime <= now:
                messages.info(request, "Etkinlik geçtiği için silemezsiniz")
                return redirect('eventdetail',slug=slug)
        if katilimcilar.exists():
            # Etkinlikte katılımcılar var, silinemez
            messages.info(request, "Etkinlikte katılımcılar bulunuyor. Bu etkinlik silinemez.")
        else:
                if request.user == etkinlik.yönetici:
                # Kullanıcı etkinlik yöneticisi ise etkinliği sil
                    etkinlik.silindi = True
                    etkinlik.save()
                    messages.info(request, "Etkinlik başarıyla silindi")
                    return redirect('home')
                else:
                    # Kullanıcı etkinlik yöneticisi değil, silme yetkisi yok
                    messages.error(request, "Bu etkinliği silme yetkiniz yok.")
    else:
        # Geçersiz istek yöntemi
        messages.error(request, "Geçersiz istek")

    return redirect('eventdetail', slug=slug)


@login_required        

@login_required  # Kullanıcının oturum açmış olması gerektiğini kontrol etmek için kullanabilirsiniz
def etkinlik_ekle(request, year=None, month=None):
    if year is None:
        year = datetime.now().year
    if month is None:
        month = datetime.now().strftime('%B')

    if request.method == "POST":
        form = EtkinlikForm(request.POST)
        if form.is_valid():
            etkinlik = form.save(commit=False)
            etkinlik.yönetici = request.user

            # Aynı gün ve saatte etkinlik kontrolü
            existing_event = request.user.profile.olusturdugu_etkinlikler.filter(gün=etkinlik.gün, saat=etkinlik.saat)
            if existing_event:
                form.add_error(None, 'Bu saatte başka bir etkinlik zaten var.')
            elif etkinlik.gün.date() < date.today():
                form.add_error('gün', 'Geçmiş tarihe etkinlik ekleyemezsiniz.')
            else:
                now = datetime.now().time()
                if etkinlik.gün.date() == date.today() and etkinlik.saat < now:
                    form.add_error('saat', 'Geçmiş saate etkinlik ekleyemezsiniz.')
                else:
                    etkinlik.save()
                    form.save_m2m()  # Many-to-many ilişkileri kaydet
                    slug = etkinlik.slug
                    request.user.profile.olusturdugu_etkinlikler.add(etkinlik)  # Kullanıcının oluşturduğu etkinliği ekleyin
                    return redirect('eventdetail', slug=slug)
    else:
        form = EtkinlikForm()

    data = create_calendar(year, month)
    return render(request, 'etkinlik/etkinlik_ekle.html', {'form': form, **data})




def get_mekanlar(request, ilce_id):
    mekanlar = Mekan.objects.filter(onayli=True,acik =True,ilce_id=ilce_id).values('id', 'adi')
    return JsonResponse(list(mekanlar), safe=False)
def register(request,year=None,month=None):
    if year is None:
        year = datetime.now().year
    if month is None:
        month = datetime.now().strftime('%B')

    data = create_calendar(year, month)
    user = request.user
    if user.is_authenticated:
        logout(request)
        return redirect('register')
    else:
        if request.method == 'POST':
            form = RegistrationForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('login')  # Kullanıcı başarıyla kaydedildikten sonra giriş sayfasına yönlendirilebilirsiniz
        else:
            form = RegistrationForm()
        return render(request, 'register.html', {'form': form, **data})


from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
def update_profile(request, year=None, month=None):
    if year is None:
        year = datetime.now().year
    if month is None:
        month = datetime.now().strftime('%B')

    data = create_calendar(year, month)

    try:
        event_user = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        user = request.user
        event_user = Profile.objects.create(user=user)

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=event_user)
        password_form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            user = request.user
            profile.user = user

            if not form.cleaned_data['profile_img']:
                profile.profile_img = event_user.profile_img

            profile.save()

            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)

            return redirect('my_profile')
    else:
        form = ProfileUpdateForm(instance=event_user)
        password_form = PasswordChangeForm(request.user)

    return render(request, 'profile/profili_güncelle.html', {'form': form, 'password_form': password_form, **data})




def katilimci_ol(request, slug):
    etkinlik = get_object_or_404(Event, slug=slug)
    katilimcilar = etkinlik.katilimcilar.all()
    now = datetime.now()
    user = request.user
    kontenjan = etkinlik.kontenjan
    event_datetime = datetime.combine(etkinlik.gün, etkinlik.saat)
    son_katilma_saati = event_datetime - timedelta(hours=1)
    if etkinlik.yönetici == request.user:
        messages.error(request, "Etkinlik yöneticisi sizsiniz")
        print('Yönetici Alanı Çalıştır')
    else:
        if etkinlik.katilimci_kontrol == True:
            if kontenjan == 0:
                messages.info(request, "Etkinlik Daha Fazla Katılımcı Kabul Etmiyor")
                print('Doğru Çalışıyor Gibi')
                return redirect('eventdetail', slug=slug)
        
        if event_datetime >= now:  # Etkinlik henüz gerçekleşmemişse
            katildigi_etkinlikler = request.user.profile.katildigi_etkinlikler.filter(gün=etkinlik.gün, saat=etkinlik.saat) # Katıldığı etkinlikleri giriş yapan kullanıcının etkinlikleri ile gün ve saat olarak filtreledim.
            if katildigi_etkinlikler.exists():
                messages.error(request, "Aynı saat ve günde zaten bir etkinliğe katıldınız. Başka bir etkinliğe katılamazsınız.")
                print('Doğru Çalışıyor Gibi')
                return redirect('eventdetail', slug=slug)
            
            if son_katilma_saati > now:
                # Kullanıcının profiline etkinliği ekle
                etkinlik.katilimcilar.add(request.user)  # Etkinlik nesnesine kullanıcıyı ekle
                request.user.profile.katildigi_etkinlikler.add(etkinlik)
                bildirim = Bildirim.objects.create(etkinlik=etkinlik, etkilesim=user, bildirim_alani=etkinlik.yönetici.profile, bildirim=f"{user.username} adlı kullanıcı {etkinlik.ad} adlı etkinliğinize katıldı.")
                etkinlik.yönetici.profile.bildirimler.add(bildirim)
                etkinlik.yönetici.profile.bildirim_sayisi += 1 
                etkinlik.yönetici.profile.save()
                bildirim.save()
                if kontenjan == 0:
                    bildirim = Bildirim.objects.create(etkinlik=etkinlik, etkilesim=user, bildirim_alani=etkinlik.yönetici.profile, bildirim=f"{etkinlik.ad} adlı etkinliğinizin kontenjanı doldu.")
                    etkinlik.yönetici.profile.bildirimler.add(bildirim)
                    etkinlik.yönetici.profile.bildirim_sayisi += 1 
                    etkinlik.yönetici.profile.save()
                    bildirim.save()
                print('Bildirim Kaydetti')
                etkinlik.yönetici.save()

                
                if etkinlik.katilimci_kontrol == True:
                    etkinlik.kontenjan -= 1
                    etkinlik.save()
                    print('Herhangi bir yere takılmadı, eklendi')
                  



            else:
                messages.info(request, "Etkinlik saatine 1 saatten az bir süre süre kaldığı için bu etkinliğe katılmanız mümkün değil!")
                print('Etkinlik Saatine 1 saatten fazla bir süre kalmadığı yer çalıştı.')
        else:
            messages.error(request, "Etkinlik günü geçtiği için bu etkinliğe katılmanız mümkün değil!")
            print('Etkinlik Gününün Geçtiği yer çalıştı.')

    return redirect('eventdetail', slug=slug)






def katilmayi_birak(request, slug):
    etkinlik = get_object_or_404(Event, slug=slug)
    kontenjan = etkinlik.kontenjan
    now = datetime.now()
    event_datetime = datetime.combine(etkinlik.gün, etkinlik.saat)
    if etkinlik.yönetici == request.user:
        messages.error(request, "Etkinlik yöneticisi sizsiniz")
        
    else:
        if event_datetime >= now:  # Etkinlik henüz gerçekleşmemişse
            etkinlik.katilimcilar.remove(request.user)  # Etkinlik nesnesinden kullanıcıyı kaldır
            request.user.profile.katildigi_etkinlikler.remove(etkinlik)  # Kullanıcının profiline etkinliği kaldır
            try:
                bildirim = Bildirim.objects.get(etkinlik=etkinlik, etkilesim=request.user)
                bildirim.delete()
            except Bildirim.DoesNotExist:
                # İstenilen kriterlere uygun Bildirim nesnesi bulunamadı
                print('Bildirim Bulunamadı')


            if etkinlik.katilimci_kontrol == True:
                etkinlik.kontenjan += 1
                etkinlik.save()
        else:
            messages.error(request, "Katıldığınız etkinliğin günü geçtiği için bu etkinlikten çıkamazsınız")
    return redirect('eventdetail', slug=slug)

            

def show_profile(request, username, year=None, month=None):
    if year is None:
        year = datetime.now().year
    if month is None:
        month = datetime.now().strftime('%B')

    data = create_calendar(year, month)
    user = User.objects.get(username=username)
    katildigi_etkinlikler = user.profile.katildigi_etkinlikler.all()
    katildigi_etkinlik_sayisi = katildigi_etkinlikler.count()
    olusturdugu_etkinlikler = user.profile.olusturdugu_etkinlikler.all()
    olusturdugu_etkinlik_sayisi = olusturdugu_etkinlikler.count()
    son_etkinlikler = olusturdugu_etkinlikler.order_by('-id')
    son_etkinliklerim = son_etkinlikler[:2]

    context = {
        'user': user,
        'katildigi_etkinlikler': katildigi_etkinlikler,
        'katildigi_etkinlik_sayisi': katildigi_etkinlik_sayisi,
        'olusturdugu_etkinlikler': olusturdugu_etkinlikler,
        'olusturdugu_etkinlik_sayisi': olusturdugu_etkinlik_sayisi,
        'son_etkinliklerim': son_etkinliklerim
    }

    context.update(data)  # data sözlüğünü context sözlüğüne güncelle

    return render(request, 'profile/show_profile.html', context)







def login_view(request,year=None,month=None):
    if year is None:
        year = datetime.now().year
    if month is None:
        month = datetime.now().strftime('%B')
        data = create_calendar(year, month)
    user = request.user
    if user.is_authenticated: #Kullanıcı giriş yapmış ve tekrar login olmaya çalışırsa logout edilir.
        
        return redirect('logout')
    else:
        if request.method == 'POST':
            
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if user is not None:
                    if hasattr(user, 'profile'):
                        return redirect('home')
                    else:
                        return redirect('update_profile')
            else:
                messages.error(request, 'Kullanıcı adı veya şifre yanlış.')
    
    return render(request, 'login.html', data)
def my_profile(request, year=None, month=None):
    if year is None:
        year = datetime.now().year
    if month is None:
        month = datetime.now().strftime('%B')
    data = create_calendar(year, month)
    user = request.user
    katildigi_etkinlikler = user.profile.katildigi_etkinlikler.all()
    katildigi_etkinlik_sayisi = katildigi_etkinlikler.count()
    olusturdugu_etkinlikler = user.profile.olusturdugu_etkinlikler.all()
    olusturdugu_etkinlik_sayisi = olusturdugu_etkinlikler.count()
    son_etkinlikler = olusturdugu_etkinlikler.order_by('-id')
    son_etkinliklerim = son_etkinlikler[:2]
    olusturdugu_etkinlik_id_list = olusturdugu_etkinlikler.values_list('id', flat=True)
    bildirimler = Bildirim.objects.filter(etkinlik_id__in=olusturdugu_etkinlik_id_list).order_by('-olusturulma_tarihi')
    context = {
        'user': user,
        'bildirimler':bildirimler,
        'katildigi_etkinlikler': katildigi_etkinlikler,
        'katildigi_etkinlik_sayisi': katildigi_etkinlik_sayisi,
        'olusturdugu_etkinlikler': olusturdugu_etkinlikler,
        'olusturdugu_etkinlik_sayisi': olusturdugu_etkinlik_sayisi,
        'son_etkinliklerim': son_etkinliklerim
    }
    context.update(data)  # data sözlüğünü context sözlüğüne güncelle
    return render(request, 'profile/my_profile.html', context)


from django.contrib import messages
@login_required
def custom_logout(request):
    user = request.user
    if user.is_authenticated:
        logout(request)
        messages.info(request, "Çıkış Yapıldı !")
        return redirect("login")
    else:
        return redirect("home")

from django.utils import timezone

from datetime import datetime, timedelta
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect, render
from .models import Event

from datetime import timedelta

from datetime import timedelta

from datetime import timedelta

def etkinlik_düzenle(request, slug, year=None, month=None):
    if year is None:
        year = datetime.now().year
    if month is None:
        month = datetime.now().strftime('%B')
    
    etkinlik = get_object_or_404(Event, slug=slug)
    kontenjan  = etkinlik.kontenjan
    now = datetime.now()
    user = request.user
    event_datetime = datetime.combine(etkinlik.gün, etkinlik.saat)
    
    if etkinlik.yönetici != user:
        messages.error(request, "Etkinlik yöneticisi siz değilsiniz.")
        return redirect('home')


    if event_datetime <= now:
        messages.error(request, "Etkinlik tarihi geçmiş olduğu için düzenleyemezsiniz.")
        return redirect('eventdetail', slug=slug)

    son_düzenleme_saati = event_datetime - timedelta(hours=1)

    if son_düzenleme_saati <= now:
        print(son_düzenleme_saati)
        print(event_datetime)
        messages.error(request, "Etkinliğe 1 saatten az bir süre kaldığı için bu etkinliği düzenleyemezsiniz.")
        return redirect('eventdetail', slug=slug)
    if request.method == "POST":
        form = EtkinlikUpdateForm(request.POST, instance=etkinlik)
        if form.is_valid():
            if form.cleaned_data['gün'].date() < date.today():
                form.add_error('gün', 'Geçmiş tarihe etkinlik ekleyemezsiniz.')
            else:
                etkinlik = form.save(commit=False)
                etkinlik.slug = slug

                if etkinlik.katilimci_kontrol:
                    etkinlik.kontenjan = form.cleaned_data['kontenjan']
                    
                else:
                    etkinlik.kontenjan = 0

                etkinlik.save()
                return redirect('eventdetail', slug=slug)


    else:
        form = EtkinlikUpdateForm(instance=etkinlik)
    print(event_datetime)
    print(son_düzenleme_saati)
    data = create_calendar(year, month)
    return render(request, 'etkinlik/etkinlik_düzenle.html', {'form': form, **data})








def mekan_guncelle(request, mekan_id,year=None,month=None):
    if year is None:
        year = datetime.now().year
    if month is None:
        month = datetime.now().strftime('%B')
    data = create_calendar(year, month)
    mekan = get_object_or_404(Mekan, id=mekan_id)
    user = request.user
    
    if user != mekan.olusturan:
        messages.warning(request, 'Bu Yer Size Ait Değil')
        return redirect('yer_listesi')
    if mekan.acik == True:
        messages.warning(request, 'Mekan Şuan Faaliyette Güncelleme İşlemi Yapılamaz')
        return redirect('mekanlar')
    else:
        if request.method == 'POST':
            form = MekanUpdateForm(request.POST, instance=mekan)
            if form.is_valid():
                form.save()
                return redirect('yer_detay', mekan.pk)
        else:
            form = MekanUpdateForm(instance=mekan)
            messages.info(request,'Yerlerde Şehir ve İlçe Güncellenmesi Yapılamıyor.Mekanı Silip Tekrar Başvuru Yapmanız Gerekir.')
            print('Hata Geliyor Htmlde yok')
        return render(request, 'etkinlik/mekan_güncelle.html', {'form': form, 'mekan': mekan,**data})
    
def sahip_oldugunuz_mekanlar(request, year=None, month=None):
    if year is None:
        year = datetime.now().year
    if month is None:
        month = datetime.now().strftime('%B')
    
    user = request.user
    mekanlar = Mekan.objects.filter(olusturan=user)
    
    data = create_calendar(year, month)
    
    return render(request, 'sahip_mekanlar.html', {'mekanlar': mekanlar, **data})

def etkinliklerim(request, year=None, month=None):
    if year is None:
        year = datetime.now().year
    if month is None:
        month = datetime.now().strftime('%B')
    
    user = request.user
    etkinlikler = Event.objects.filter(yönetici=user)
    
    data = create_calendar(year, month)
    
    return render(request, 'etkinliklerim.html', {'etkinlikler': etkinlikler, **data})

from django.http import Http404

def etkinlikten_at(request, slug, pk):
    etkinlik = get_object_or_404(Event, slug=slug)
    katilimci = get_object_or_404(User, pk=pk)
    event_datetime = datetime.combine(etkinlik.gün, etkinlik.saat)
    now = datetime.now()
    son_atma_tarihi = event_datetime - timedelta(hours=1)
    if etkinlik.yönetici == request.user:
        
        if event_datetime <= now:
                print(event_datetime)
                print(son_atma_tarihi)
                messages.success(request, "Geçmiş bir etkinlikte katılımıcıyı düzenleyemezsiniz.")
                return redirect('eventdetail', slug=slug)
        else:
            if son_atma_tarihi <= now:
                print(son_atma_tarihi)
                print(event_datetime)
                messages.error(request, "Etkinliğe 1 saatten az bir süre kaldığı için bu etkinliği düzenleyemezsiniz.")
                return redirect('eventdetail', slug=slug)
            else:
                    if request.method == "POST":
                        # Etkinlikten kullanıcıyı çıkar
                        etkinlik.katilimcilar.remove(katilimci)
                        katilimci.profile.katildigi_etkinlikler.remove(etkinlik)
                        messages.success(request, 'Kullanıcı etkinlikten çıkarıldı.')
                        etkinlik.kontenjan += 1
                        etkinlik.save()
                        return redirect('eventdetail', slug=slug)
                    else:
                        raise Http404("Geçersiz istek yöntemi.")
    else:
                messages.error(request, 'Bu etkinlik size ait değil.')
                return redirect('eventdetail', slug=slug)
def yorum_yap(request, slug):
    etkinlik = get_object_or_404(Event, slug=slug)
    user = request.user
    slug = etkinlik.slug
    event_datetime = datetime.combine(etkinlik.gün, etkinlik.saat)
    now = datetime.now()


    if request.method == 'POST':
        if user.is_authenticated:
            if etkinlik.katilimcilar.filter(id=user.id).exists():
                form = YorumForm(request.POST)
                if form.is_valid():
                    yorum = form.save(commit=False)
                    yorum.event = etkinlik
                    yorum.yorum_sahibi = user
                    yorum.save()
                    bildirim = Bildirim.objects.create(etkinlik=etkinlik, etkilesim=user, bildirim_alani=etkinlik.yönetici.profile, bildirim=f"{user.username} adlı kullanıcı {etkinlik.ad} yorum yaptı.")
                    etkinlik.yönetici.profile.bildirimler.add(bildirim)
                    etkinlik.yönetici.profile.bildirim_sayisi += 1 
                    etkinlik.yönetici.profile.save()
                    bildirim.save()
                    return redirect('eventdetail', slug=slug)
            else:
                messages.info(request, 'Katılımcı Olmadığınız Etkinliğe Yorum Yapamazsınız')
                return redirect('eventdetail', slug=slug)
    else:
        messages.info(request, 'Yorum Gönderildi')
    return redirect('eventdetail', slug=slug)

def yorum_sil(request, pk):
    yorum = get_object_or_404(Yorum, pk=pk)
    user = request.user
    etkinlik_yorum = yorum.event
    slug = etkinlik_yorum.slug

    if request.method == 'POST':
        if user.is_authenticated:
            if yorum.yorum_sahibi == user:
                yorum.silindi = True
                yorum.save()
                print('buraya geldi')
                messages.success(request, 'Yorum başarıyla silindi.')
            else:
                messages.warning(request, 'Yorum senin mi ulan dallama')
                print('takıldı')
        else:
            messages.warning(request, 'Yorum yapabilmek için giriş yapmalısınız.')
            print('burada')
        return redirect('eventdetail', slug=slug)

    return redirect('eventdetail', slug=slug)

def cevap_ver(request, pk, slug):
    yorum = get_object_or_404(Yorum, pk=pk)
    etkinlik = get_object_or_404(Event, slug=slug)
    slug = etkinlik.slug
    user = request.user

    if request.method == 'POST':
        if user.is_authenticated:
            form = CevapForm(request.POST)
            if form.is_valid():
                cevap = form.save(commit=False)
                cevap.yorum = yorum  # Değişiklik burada yapıldı
                cevap.cevapsahibi = user
                cevap.save()
                messages.success(request, 'Cevap gönderildi')
            else:
                print(form.errors)
                messages.error(request, 'Geçersiz bir cevap gönderdiniz')
        else:
            messages.info(request, 'Cevap vermek için giriş yapmalısınız')
    return redirect('eventdetail', slug=slug)

def mekan_sil(request, pk):
    mekan = get_object_or_404(Mekan, pk=pk)
    etkinlikler = Event.objects.filter(mekan=mekan)
    
    if mekan.olusturan == request.user:
        if etkinlikler.exists():
            messages.info(request, "Bu mekanda etkinlikler bulunuyor. Bu mekan silinemez.")
            return redirect('mekanlar')
        else:
            mekan.delete()
            messages.success(request, "Mekan başarıyla silindi.")
            return redirect('home')
    else:
        messages.warning(request, "Bu işlemi gerçekleştirmek için yetkiniz yok.")
        return redirect('home')

def mekani_ac(request,pk):
    mekan = get_object_or_404(Mekan,pk=pk)

    if mekan.olusturan == request.user:
       if mekan.acik == True:
        messages.success(request, "Bu mekan zaten faaliyette.")
        return redirect('mekanlar')
       else:
        mekan.acik = True
        mekan.save()
        messages.success(request, "Mekan başarıyla açıldı.")
        return redirect('yer_detay',pk=mekan.pk)
    else:
        messages.error(request, "Mekan size ait değil.")
        return redirect('mekanlar')
def mekani_kapat(request,pk):
    mekan = get_object_or_404(Mekan,pk=pk)

    if mekan.olusturan == request.user:
       if mekan.acik == False:
        messages.success(request, "Bu mekan zaten kapalı.")
        return redirect('mekanlar')
       else:
        mekan.acik = False
        mekan.save()
        messages.success(request, "Mekan başarıyla kapatıldı.")
        return redirect('mekanlar')
    else:
        messages.error(request, "Mekan size ait değil.")
        return redirect('mekanlar')

def olumlu_oy(request, pk):
    mekan = get_object_or_404(Mekan, pk=pk)
    user = request.user
    
    if user == mekan.olusturan:
        messages.error(request, "Kendinize ait bir yerde oy kullanamazsınız")
        return JsonResponse({'success': True})
    
    # Kullanıcının daha önce olumlu oy vermişse
    if mekan.olumlu_oy_kullananlar.filter(id=user.id).exists():
        mekan.olumlu_oy -= 1
        mekan.olumlu_oy_kullananlar.remove(user)
        mekan.save()  # Oy kaldırıldı, değişikliği kaydet
    
        print('Mekan Kaydedildi oy kullanlardan olumlu oy düştü')
        return JsonResponse({'success': True})
    
    # Kullanıcının daha önce olumsuz oy vermişse, olumsuz oyunu kaldır
    if mekan.olumsuz_oy_kullananlar.filter(id=user.id).exists():
        mekan.olumsuz_oy -= 1
        mekan.olumsuz_oy_kullananlar.remove(user)
    
    mekan.olumlu_oy += 1
    mekan.olumlu_oy_kullananlar.add(user)
    mekan.save()
    
    print('Olumlu oy#2')
    return JsonResponse({'success': True})



def olumsuz_oy(request, pk):
    mekan = get_object_or_404(Mekan, pk=pk)
    user = request.user
    
    if user == mekan.olusturan:
        messages.error(request, "Kendinize ait bir yerde oy kullanamazsınız")
        return JsonResponse({'success': True})
    
    if mekan.olumsuz_oy_kullananlar.filter(id=user.id).exists():
        # Kullanıcı zaten olumsuz oy vermiş, oy kaldırılıyor
        mekan.olumsuz_oy -= 1
        mekan.olumsuz_oy_kullananlar.remove(user)
        print('Kullanıcı zaten olumsuz oy vermiş, oy kaldırılıyor')
    else:
        # Kullanıcı ilk defa olumsuz oy kullanıyor
        if mekan.olumlu_oy_kullananlar.filter(id=user.id).exists():
            # Kullanıcı daha önce olumlu oy vermişse, olumlu oyunu kaldır
            mekan.olumlu_oy -= 1
            mekan.olumlu_oy_kullananlar.remove(user)
        
        mekan.olumsuz_oy += 1
        mekan.olumsuz_oy_kullananlar.add(user)
        print('Kullanıcı ilk defa olumsuz oy kullanıyor')
    
    mekan.save()
    return JsonResponse({'success': True})

def mekan_begeni_durumu(request, pk):
    mekan = get_object_or_404(Mekan, pk=pk)
    user = request.user

    if mekan.olumlu_oy_kullananlar.filter(id=user.id).exists():
        return JsonResponse({'durum': 'liked'})
    elif mekan.olumsuz_oy_kullananlar.filter(id=user.id).exists():
        return JsonResponse({'durum': 'disliked'})
    else:
        return JsonResponse({'durum': 'none'})