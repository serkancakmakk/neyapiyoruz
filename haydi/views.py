
import time
from django.shortcuts import redirect, render
import locale
import calendar
from .forms import CevapForm, EtkinlikUpdateForm, MekanUpdateForm, MyForm, ProfileUpdateForm, RegistrationForm, YorumForm
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
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
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
    permission = Permission.objects.get(codename='event_olustur')
    user = User.objects.get(username=user.profile.username)
    user.profile.yetkiler.add(permission)
    user.save()
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


    
def create_calendar(year, month):
    locale.setlocale(locale.LC_ALL, 'tr_TR.UTF-8')
    month = month.capitalize()
    month_names = list(calendar.month_name)
    month_number = month_names.index(month) if month in month_names else 1

    cal = []

    now = datetime.now()
    current_year = now.year
    current_month = calendar.month_name[now.month]
    current_day = now.day

    if month_number == 12:
        next_month_number = 1
        next_year = year + 1
    else:
        next_month_number = month_number + 1
        next_year = year

    # Takvim verilerini oluştur
    cal = calendar.monthcalendar(year, month_number)

    return {
        "year": year,
        "month": month,
        "month_number": month_number,
        "current_month": current_month,
        "current_year": current_year,
        "current_day": current_day,
        "cal": cal,
        "next_month": calendar.month_name[next_month_number].lower(),
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
        engellendin = etkinlik.yönetici.profile.engelli_listesi.filter(pk=request.user.pk).exists()
        

        if user.is_authenticated:
            if etkinlik.silindi:
                return render(request, 'etkinlik/etkinlik_silindi.html', {'etkinlik': etkinlik, **data})
            if engellendin:
                messages.success(request,'Yönetici sizi engelledi bu etkinliği görüntüleyemezsiniz')
                return render(request, 'home.html')
            else:
                return render(request, 'etkinlik/eventdetail.html', {'etkinlik': etkinlik, 'katilimcilar': katilimcilar,
                                                                     'profile': profile, 'form': form,
                                                                     'yorumlar': sayfa, 'sayfa': sayfa, **data,
                                                                     'son_yorumlar': son_yorumlar,
                                                                     'cevapform': cevapform,
                                                                     'cevaplar_listesi': cevaplar_listesi})
        else:
            return redirect('login')

@login_required
def home(request, year=None, month=None):
    if year is None:
        year = datetime.now().year
    if month is None:
        month = datetime.now().strftime('%B')
    form = MyForm()
    calendar_data = create_calendar(year, month)
    day = calendar_data['current_day']  # Güncel günü alın
    now = datetime.now()
    current_day = now.day


    if request.user.is_authenticated:
        user = request.user
        engellenenler = user.profile.engelli_listesi.values_list('pk', flat=True)
        engellenen_profiller = Profile.objects.filter(user_id__in=engellenenler)
        engellendigim_profiller = Profile.objects.filter(engelli_listesi=user)
        takip_ettiklerim = request.user.profile.takip_ettiklerim.all()

        takip_ettiklerim = request.user.profile.takip_ettiklerim.all()

        etkinlikler = Event.objects.exclude(
            Q(yönetici__profile__in=engellenen_profiller) |
            Q(yönetici__profile__in=engellendigim_profiller)
        ).filter(
            Q(yönetici__in=takip_ettiklerim)
        )
        sehirler = Region.objects.all()[:10]
    else:
        etkinlikler = None
        sehirler = None

        
    context = {
        'current_day': current_day,
        'calendar': calendar_data['cal'],
        'year': calendar_data['year'],
        'month': calendar_data['month'],
        'day': day,  # Güncel günü context'e ekle
        'events': etkinlikler,
        'sehirler': sehirler,
        'form': form,
    }
    
    return render(request, 'home.html', context)





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
# def your_view(request):
#     # Yetkileri oluşturmak için view fonksiyonuna kodu ekleyin
#     try:
#         content_type1 = ContentType.objects.get_for_model(Event)
#         permission1, created1 = Permission.objects.get_or_create(
#             codename='add_event',
#             name='Event Oluştur',
#             content_type=content_type1
#         )

#         content_type2 = ContentType.objects.get_for_model(Başka_BİR_YETKİ)
#         permission2, created2 = Permission.objects.get_or_create(
#             codename='add_baska_yetki',
#             name='Başka Yetki Oluştur',
#             content_type=content_type2
#         )

#         content_type3 = ContentType.objects.get_for_model(Başka_BİR_YETKİ_2)
#         permission3, created3 = Permission.objects.get_or_create(
#             codename='add_baska_yetki_2',
#             name='Başka Yetki 2 Oluştur',
#             content_type=content_type3
#         )

#     except Permission.DoesNotExist:
#         # Yetki zaten varsa yapılacak işlemler
#         pass

#     # Diğer view kodlarınızı buraya ekleyin
#     # ...

#     # Response döndürün


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
            return redirect('update_profile')
    else:
        form = ProfileUpdateForm(instance=event_user)
        password_form = PasswordChangeForm(request.user)

    return render(request, 'profile/profili_güncelle.html', {'form': form, 'password_form': password_form, **data})




def katilimci_ol(request, slug):
    etkinlik = get_object_or_404(Event, slug=slug)
    user = request.user
    engellendin = etkinlik.yönetici.profile.engelli_listesi.filter(pk=request.user.pk).exists()
    
    katilimcilar = etkinlik.katilimcilar.all()
    now = datetime.now()
    katildigi_etkinlikler = request.user.profile.katildigi_etkinlikler.filter(gün=etkinlik.gün, saat=etkinlik.saat)
    kontenjan = etkinlik.kontenjan
    event_datetime = datetime.combine(etkinlik.gün, etkinlik.saat)
    son_katilma_saati = event_datetime - timedelta(hours=1)
    if etkinlik.yönetici == request.user:
        messages.error(request, "Etkinlik yöneticisi sizsiniz")
        print('Yönetici Alanı Çalıştır')
    if etkinlik.takipçiye_özel:
        if not etkinlik.yönetici.profile.takipçiler.filter(pk=user.pk).exists():
            messages.error(request, "Takipçisi Olmadığınız için katilamazsınız.")
            return redirect('eventdetail', slug=slug)
    if engellendin:
            messages.error(request, "Etkinlik Yöneticisinin Engellenen Listesindesin Bu Etkinliğe Katılamazsın.")
            return redirect('home')
    if event_datetime <= now:  # Etkinlik henüz gerçekleşmemişse
        messages.error(request, "Etkinlik günü geçtiği için bu etkinliğe katılmanız mümkün değil!")
        return redirect('eventdetail', slug=slug)
    if katildigi_etkinlikler.exists():
            messages.error(request, "Aynı saat ve günde zaten bir etkinliğe katıldınız. Başka bir etkinliğe katılamazsınız.")
            print('Doğru Çalışıyor Gibi')
            return redirect('eventdetail', slug=slug)
    else:
            
        if son_katilma_saati < now:
                messages.info(request, "Etkinlik saatine 1 saatten az bir süre süre kaldığı için bu etkinliğe katılmanız mümkün değil!")
                print('Etkinlik Saatine 1 saatten fazla bir süre kalmadığı yer çalıştı.')
                return redirect('eventdetail', slug=slug)
        if etkinlik.katilimci_kontrol == True:
            if etkinlik.kontenjan == 0:
                messages.info(request, "kontenjan yok")
                print('Etkinlik Saatine 1 saatten fazla bir süre kalmadığı yer çalıştı.')
                return redirect('eventdetail', slug=slug)
        if kontenjan == 0:
            bildirim = Bildirim.objects.create(etkinlik=etkinlik, etkilesim=etkinlik.yönetici, bildirim_alani=etkinlik.yönetici.profile, bildirim=f"{etkinlik.ad} adlı etkinliğinizin kontenjanı doldu.")
            etkinlik.yönetici.profile.bildirimler.add(bildirim)
            etkinlik.yönetici.profile.bildirim_sayisi += 1 
            etkinlik.yönetici.profile.save()
            bildirim.save()
        else:
            
                                    # Kullanıcının profiline etkinliği ekle
            etkinlik.katilimcilar.add(request.user)  # Etkinlik nesnesine kullanıcıyı ekle
            request.user.profile.katildigi_etkinlikler.add(etkinlik)
            bildirim = Bildirim.objects.create(etkinlik=etkinlik, etkilesim=user, bildirim_alani=etkinlik.yönetici.profile, bildirim=f"{user.username} adlı kullanıcı {etkinlik.ad} adlı etkinliğinize katıldı.")
            etkinlik.yönetici.profile.bildirimler.add(bildirim)
            etkinlik.yönetici.profile.bildirim_sayisi += 1 
            etkinlik.kontenjan -= 1
            etkinlik.yönetici.profile.save()
            bildirim.save()
            print('Bildirim Kaydetti')
            etkinlik.save()
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
    if user == request.user:
        return redirect('my_profile')
    
    oy_durumu_pozitif =  user.profile.pozitif_oylar.filter(pk=request.user.pk).exists()
    oy_durumu_negatif =  user.profile.negatif_oylar.filter(id=request.user.pk).exists()
    katildigi_etkinlikler = user.profile.katildigi_etkinlikler.all()
    katildigi_etkinlik_sayisi = katildigi_etkinlikler.count()
    olusturdugu_etkinlikler = user.profile.olusturdugu_etkinlikler.all()
    olusturdugu_etkinlik_sayisi = olusturdugu_etkinlikler.count()
    son_etkinlikler = olusturdugu_etkinlikler.order_by('-id')
    son_etkinliklerim = son_etkinlikler[:2]
    engelli = request.user.profile.engelli_listesi.filter(pk=user.pk).exists()
    engellendin = user.profile.engelli_listesi.filter(pk=request.user.pk).exists()
    takipte = request.user.profile.takip_ettiklerim.filter(pk=user.pk).exists()
    pozitif_oylar = user.profile.pozitif_oylar.all() 
    rating = pozitif_oylar.count() *5



    context = {
        'user': user,
        'engelli':engelli,
        'takipte':takipte,
        'rating':rating,
        'pozitif_oylar':pozitif_oylar,
        'oy_durumu_pozitif':oy_durumu_pozitif,
        'oy_durumu_negatif':oy_durumu_negatif,
        'engellendin':engellendin,
        'katildigi_etkinlikler': katildigi_etkinlikler,
        'katildigi_etkinlik_sayisi': katildigi_etkinlik_sayisi,
        'olusturdugu_etkinlikler': olusturdugu_etkinlikler,
        'olusturdugu_etkinlik_sayisi': olusturdugu_etkinlik_sayisi,
        'son_etkinliklerim': son_etkinliklerim
    }

    context.update(data)
    return render(request, 'profile/show_profile.html', context)





from django.contrib.auth import login as auth_login
from django.shortcuts import redirect

def login_view(request, year=None, month=None):
    if year is None:
        year = datetime.now().year
    if month is None:
        month = datetime.now().strftime('%B')
    data = create_calendar(year, month)
    user = request.user

    if user.is_authenticated: 
        return redirect('logout')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)

                if hasattr(user, 'profile'):
                    return redirect('home')
                else:
                    Profile.objects.create(user=user)  # Profil oluştur
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
    takip_listesi = request.user.profile.takip_ettiklerim.all()
    takipçi_listesi = request.user.profile.takipçiler.all()
    takip_sayisi = 10
    paginatör = Paginator(takip_listesi,takip_sayisi )
    sayfa_numarasi = request.GET.get('sayfa')  # URL parametresinden sayfa numarasını alın
    sayfa = paginatör.get_page(sayfa_numarasi)

    context = {
        'user': user,
        'sayfa':sayfa,
        'takip_listesi':takip_listesi,
        'takipçi_listesi':takipçi_listesi,
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
from django.shortcuts import render
# def gundetay(request):
#     selected_date = request.GET.get('selected_date')
#     return redirect('gundetay_selected', selected_date=selected_date)
# from django.shortcuts import render

from datetime import datetime

def gundetay(request, day, month, year):
    # Tarihi parçalara ayırma
    day = int(day)
    year = int(year)
    # Ayı dize olarak kullanma
    selected_date = datetime.strptime(month, '%B')
    month = selected_date.month
    # Etkinlikleri tarihlerine göre filtreleme
    selected_date = datetime(year, month, day)
    etkinlikler = Event.objects.filter(gün=selected_date)
    etkinlik_sayisi = 3
    #tüm etkinlikler için paginatörü ayarla
    paginatör = Paginator(etkinlikler, etkinlik_sayisi)
    sayfa_numarasi = request.GET.get('sayfa')  # URL parametresinden sayfa numarasını alın
    sayfa = paginatör.get_page(sayfa_numarasi)
    #tüm etkinlikler için paginatörü ayarla
    # Kullanıcının ilişkilendirildiği profilü al
    profile = request.user.profile
    # Katıldığı etkinlikleri filtreleme
    katildigi_etkinlikler = etkinlikler.filter(katilimcilar=request.user)
    tüm_etkinlikler = etkinlikler.filter(gün=selected_date)
    olusturdugu_etkinlikler = etkinlikler.filter(yönetici=request.user)
    # Oluşturduğu etkinlikleri filtreleme
    
    paginatörkatildigi = Paginator(katildigi_etkinlikler, etkinlik_sayisi)
    katildigi_sayfa_numarasi = request.GET.get('katildigi_sayfa'),

    paginatörolusturdugu = Paginator(olusturdugu_etkinlikler, etkinlik_sayisi)
    olusturdugu_sayfa_numarasi = request.GET.get('olusturdugu_sayfa')
    
    katildigi_sayfa = paginatörkatildigi.get_page(katildigi_sayfa_numarasi)
    olusturdugu_sayfa = paginatörolusturdugu.get_page(olusturdugu_sayfa_numarasi)
    context = {
        'katildigi_sayfa': katildigi_sayfa,
        'olusturdugu_sayfa': olusturdugu_sayfa,
        'sayfa': sayfa,
        'selected_date': selected_date,
        'etkinlikler': etkinlikler,
        'katildigi_etkinlikler': katildigi_etkinlikler,
        'olusturdugu_etkinlikler': olusturdugu_etkinlikler,
        'tüm_etkinlikler':tüm_etkinlikler,
    }

    return render(request, 'gun_detay.html', context)

from django.shortcuts import redirect

from django.shortcuts import redirect

def engelle(request, pk):
    user = request.user
    engellenen = get_object_or_404(User, pk=pk)
    takip_edilen = get_object_or_404(User,pk=pk)
    username = engellenen.profile.username
    takipte = takip_edilen.profile.takipçiler.filter(pk=user.pk).exists()
    if request.method == "POST":
       if request.user.profile.engelli_listesi.filter(pk=engellenen.pk).exists():
            
            user.profile.engelli_listesi.remove(engellenen.pk)
            if Bildirim.objects.filter(user=takip_edilen, etkilesim=user).exists():
                bildirim = Bildirim.objects.get(user=takip_edilen, etkilesim=user)
                bildirim.delete()
                return redirect('show_profile', username=username)
            else:
                print('çalıştı engel kaldır')
                return redirect('show_profile', username=username)
   
       else:
            user.profile.engelli_listesi.add(engellenen.pk)
            user.profile.takip_ettiklerim.remove(takip_edilen.pk)
            takip_edilen.profile.takipçiler.remove(user.pk)
            if Bildirim.objects.filter(user=takip_edilen, etkilesim=user).exists():
                bildirim = Bildirim.objects.get(user=takip_edilen, etkilesim=user)
                bildirim.delete()
                return redirect('show_profile', username=username)
            else:
                print('çalıştı')
                return redirect('show_profile', username=username)
    else:
            return redirect('show_profile', username=username)
def takip_et(request,pk):
    user = request.user
    takip_edilen = get_object_or_404(User,pk=pk)
    engellendin = takip_edilen.profile.engelli_listesi.filter(pk=request.user.pk).exists()
    takipte = takip_edilen.profile.takipçiler.filter(pk=user.pk).exists()
    username = takip_edilen.profile.username
    if request.method == "POST":
        if engellendin:
            messages.error(request, "Kullanıcı sizi engelledi")
        elif takipte:
            bildirim = Bildirim.objects.get(user=takip_edilen, etkilesim=user)
            bildirim.delete()
            user.profile.takip_ettiklerim.remove(takip_edilen.pk)
            takip_edilen.profile.takipçiler.remove(user.pk)
            takip_edilen.profile.bildirim_sayisi -= 1 
        else:
            user.profile.takip_ettiklerim.add(takip_edilen.pk)
            takip_edilen.profile.takipçiler.add(user.pk)
            bildirim = Bildirim.objects.create(user=takip_edilen,etkilesim=user, bildirim_alani=takip_edilen.profile, bildirim=f"{user.username} adlı kullanıcı sizi takip etti.")
            takip_edilen.profile.bildirimler.add(bildirim)
            takip_edilen.profile.bildirim_sayisi += 1 
            bildirim.save()
        
        return redirect(request.META.get('HTTP_REFERER')) # Hangi sayfadan geldiysen ona yönlendiriyor
    
    return HttpResponse()
        
def takipciyi_cikar(request,pk):
    user = request.user
    takip_eden = get_object_or_404(User,pk=pk)
    if request.method == "POST":
        user.profile.takipçiler.remove(takip_eden.pk)
        takip_eden.profile.takip_ettiklerim.remove(user.pk)
        user.profile.save()
        return redirect('my_profile')
    else:
        return redirect(request.META.get('HTTP_REFERER')) # Hangi sayfadan geldiysen ona yönlendiriyor

def profil_pozitif_oy(request, pk):
    oy_veren = request.user
    oy_alan = get_object_or_404(User, pk=pk)
    
    if request.method == "POST":
        if oy_alan.profile.takipçiler.filter(pk=oy_veren.pk).exists():
            if oy_alan.profile.negatif_oylar.filter(pk=oy_veren.pk).exists():
                oy_alan.profile.negatif_oylar.remove(oy_veren.pk)
                oy_alan.profile.pozitif_oylar.add(oy_veren.pk)
                oy_alan.profile.save()
                return redirect(request.META.get('HTTP_REFERER'))  # Hangi sayfadan geldiysen ona yönlendiriyor
            # oy_veren oy_alan'ı takip ediyor
            if not oy_alan.profile.pozitif_oylar.filter(pk=oy_veren.pk).exists():
                    oy_alan.profile.pozitif_oylar.add(oy_veren.pk)
                    oy_alan.profile.save()
            else:
                    oy_alan.profile.pozitif_oylar.remove(oy_veren.pk)
                    oy_alan.profile.save()
                
            return redirect(request.META.get('HTTP_REFERER'))  # Hangi sayfadan geldiysen ona yönlendiriyor
        else:
            messages.success(request, 'Sadece takip ettiğiniz kişiler için oy verebilirsiniz')
            return redirect(request.META.get('HTTP_REFERER'))  # Hangi sayfadan geldiysen ona yönlendiriyor
def profil_negatif_oy(request, pk):
    oy_veren = request.user
    oy_alan = get_object_or_404(User, pk=pk)
    
    if request.method == "POST":
        if oy_alan.profile.takipçiler.filter(pk=oy_veren.pk).exists():
            if oy_alan.profile.pozitif_oylar.filter(pk=oy_veren.pk).exists():
                oy_alan.profile.pozitif_oylar.remove(oy_veren.pk)
                oy_alan.profile.negatif_oylar.add(oy_veren.pk)
                oy_alan.profile.save()
                return redirect(request.META.get('HTTP_REFERER'))  # Hangi sayfadan geldiysen ona yönlendiriyor
            else:
            # oy_veren oy_alan'ı takip ediyor
                if not oy_alan.profile.negatif_oylar.filter(pk=oy_veren.pk).exists():
                    oy_alan.profile.negatif_oylar.add(oy_veren.pk)
                    oy_alan.profile.save()
                else:
                    oy_alan.profile.negatif_oylar.remove(oy_veren.pk)
                    oy_alan.profile.save()
                
                return redirect(request.META.get('HTTP_REFERER'))  # Hangi sayfadan geldiysen ona yönlendiriyor
        else:
                messages.success(request, 'Sadece takip ettiğiniz kişiler için oy verebilirsiniz')
                return redirect(request.META.get('HTTP_REFERER'))  # Hangi sayfadan geldiysen ona yönlendiriyor


        