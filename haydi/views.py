
import time
from django.shortcuts import redirect, render
import locale
import calendar
from .forms import ProfileUpdateForm, RegistrationForm
from django.contrib.auth.models import User
from django.contrib.auth import logout
from calendar import HTMLCalendar
from datetime import date, datetime
from django.urls import reverse
from .forms import EtkinlikForm, MekanForm
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from cities_light.models import City,Region,SubRegion
from django.template.loader import render_to_string
from .models import Mekan,Event, Profile
from .forms import MekanForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

def get_ilceler(request, sehir_id):
    ilceler = SubRegion.objects.filter(region_id=sehir_id).values('id', 'name')
    return JsonResponse(list(ilceler), safe=False)
# Create your views here.
@login_required 
def mekanekle(request,year=None, month=None):
    if year is None:
        year = datetime.now().year
    if month is None:
        month = datetime.now().strftime('%B')
    submitted = False
    if request.method =="POST":
        form = MekanForm(request.POST)
        if form.is_valid():
            yer = form.save(commit=False)
            if request.user.is_authenticated:
                yer.sahip = request.user.username
                yer.save()
                submitted = True
                return HttpResponseRedirect(reverse('mekanekle') + '?submitted=True')
    else:
        form = MekanForm()  # Bu satır else bloğuna taşındı
        print(form.errors)  # Hata mesajlarını göstermek için print ekledim
        
    if 'submitted' in request.GET:
        submitted= True
    data = create_calendar(year, month)
    return render(request,'yer_ekle.html',{'form':form,**data,'submitted':submitted,'errors': form.errors})


    
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

    mekan = get_object_or_404(Mekan, pk=pk)
    etkinlikler = mekan.etkinlikler.exclude(silindi=True)

    data = create_calendar(year, month)
    return render(request, 'etkinlik/yer_detay.html', {'mekan': mekan, 'etkinlikler': etkinlikler, **data})

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
        month = datetime.now().strftime('%B')
        data = create_calendar(year, month)
        etkinlik = get_object_or_404(Event, slug=slug)
        katilimcilar = etkinlik.katilimcilar.all()
    if user.is_authenticated: #login decarotor yerine kullanıcının giriş yapıp yapmadığını kendim kontrol ettim
        if etkinlik.silindi== True:
            return render(request, 'etkinlik/etkinlik_silindi.html', {'etkinlik': etkinlik,**data})

        else:
            return render(request, 'etkinlik/eventdetail.html', {'etkinlik': etkinlik, 'katilimcilar': katilimcilar, **data})
    else:
        return redirect('login')

    

def home(request, year=None, month=None):
    name = "Serkan"
    # Varsayılan olarak geçerli yıl ve ayı ata
    if year is None:
        year = datetime.now().year
    if month is None:
        month = datetime.now().strftime('%B')

    data = create_calendar(year, month)

    data["name"] = name

    # Şehirleri sorgula ve context'e ekle
    sehirler = Region.objects.all()[:10]
    data["sehirler"] = sehirler

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
    
    if request.method == "POST":
        if etkinlik.yönetici == request.user:
            etkinlik.silindi = True
            etkinlik.save()
            messages.info(request, "Etkinlik Başarıyla Silindi")
            return redirect('home')
            
        else:
            messages.error(request, "Bu etkinliği silme yetkiniz yok.")
    return redirect('eventdetail', slug=slug)   
@login_required        
def etkinlik_ekle(request,year=None, month=None):
    if year is None:
        year = datetime.now().year
    if month is None:
        month = datetime.now().strftime('%B')
    if request.method =="POST":
        form = EtkinlikForm(request.POST)
        if form.is_valid():
            etkinlik = form.save(commit=False)  # Nesneyi kaydet, ancak veritabanına henüz gönderme
            etkinlik.yönetici = request.user  # Yöneticiyi ayarla
            if etkinlik.gün.date() < date.today(): # Günü kontrol et
                form.add_error('gün', 'Geçmiş tarihe etkinlik ekleyemezsiniz.')
            else:
                etkinlik.save()
                slug = etkinlik.slug 
                request.user.profile.olusturdugu_etkinlikler.add(etkinlik)  # Kullanıcının profiline etkinliği ekle
                return redirect('eventdetail', slug=slug)
    else:
        form = EtkinlikForm()  # Bu satır else bloğuna taşındı
        print(form.errors)  # Hata mesajlarını göstermek için print ekledim
        
    data = create_calendar(year, month)
    return render(request,'etkinlik/etkinlik_ekle.html',{'form':form,**data,'errors': form.errors})

def get_mekanlar(request, ilce_id):
    mekanlar = Mekan.objects.filter(onayli=True,ilce_id=ilce_id).values('id', 'adi')
    return JsonResponse(list(mekanlar), safe=False)
def register(request,year=None,month=None):
    if year is None:
        year = datetime.now().year
    if month is None:
        month = datetime.now().strftime('%B')

    data = create_calendar(year, month)
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
        event_user = None

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=event_user)
        password_form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid() and password_form.is_valid():
            profile = form.save(commit=False)
            if not profile.profile_img:  # Eğer resim alanı boş bırakıldıysa
             profile.profile_img = event_user.profile_img  # Mevcut profil resmini koru
        user = request.user  # user değişkenini tanımla
        profile.user = user
        profile.save()
        update_session_auth_hash(request, user)
        return redirect('my_profile')
    else:
            form = ProfileUpdateForm(instance=event_user)
            password_form = PasswordChangeForm(request.user)

    return render(request, 'profile/profili_güncelle.html', {'form': form, 'password_form': password_form, **data})

def katilimci_ol(request, slug):
    etkinlik = get_object_or_404(Event, slug=slug)
    katilimcilar = etkinlik.katilimcilar.all()
    katilimci_sayisi = katilimcilar.count()
    now = datetime.now()
    event_datetime = datetime.combine(etkinlik.gün, etkinlik.saat)
    # if katilimci_sayisi == -1:
    #     messages.error(request, "Katilimci Sayisi Doldu")
    #     return redirect('eventdetail', slug=slug)
    # else:
    if etkinlik.yönetici == request.user:
            messages.error(request, "Etkinlik yöneticisi sizsiniz")
            
    else:
            if event_datetime >= now:  # Etkinlik henüz gerçekleşmemişse
                etkinlik.katilimcilar.add(request.user)  # Etkinlik nesnesine kullanıcıyı ekle
                request.user.profile.katildigi_etkinlikler.add(etkinlik)  # Kullanıcının profiline etkinliği ekle
            else:
                messages.error(request, "Etkinlik günü geçtiği için bu etkinliğe katılmanız mümkün değil!")
    return redirect('eventdetail', slug=slug)



def katilmayi_birak(request, slug):
    etkinlik = get_object_or_404(Event, slug=slug)
    
    now = datetime.now()
    event_datetime = datetime.combine(etkinlik.gün, etkinlik.saat)
    if etkinlik.yönetici == request.user:
        messages.error(request, "Etkinlik yöneticisi sizsiniz")
        
    else:
        if event_datetime >= now:  # Etkinlik henüz gerçekleşmemişse
            etkinlik.katilimcilar.remove(request.user)  # Etkinlik nesnesinden kullanıcıyı kaldır
            request.user.profile.katildigi_etkinlikler.remove(etkinlik)  # Kullanıcının profiline etkinliği kaldır
        else:
            messages.error(request, "Katıldığınız etkinliğin günü geçtiği için bu etkinlikten çıkamazsınız")
    return redirect('eventdetail', slug=slug)

            

def show_profile(request, username, year=None, month=None):
    if year is None:
        year = datetime.now().year
    if month is None:
        month = datetime.now().strftime('%B')
    try:
        data = create_calendar(year, month)
        user = User.objects.get(username=username)
        profile = Profile.objects.get(user=user)
        katildigi_etkinlikler = profile.katildigi_etkinlikler.all()
        katildigi_etkinlik_sayisi = katildigi_etkinlikler.count()
        olusturdugu_etkinlikler = profile.olusturdugu_etkinlikler.all()
        olusturdugu_etkinlik_sayisi = olusturdugu_etkinlikler.count()
        context = {
            'user': user,
            'profile': profile,
            'katildigi_etkinlikler': katildigi_etkinlikler,
            'katildigi_etkinlik_sayisi': katildigi_etkinlik_sayisi,
            'olusturdugu_etkinlikler': olusturdugu_etkinlikler,
            'olusturdugu_etkinlik_sayisi': olusturdugu_etkinlik_sayisi
        }
    except User.DoesNotExist:
        messages.warning(request, "Kullanıcı Bulunamadı.")
        return redirect('home')
    except Profile.DoesNotExist:
        return render(request, 'profile/profile_not_found.html')

    return render(request, 'profile/show_profile.html', context)






def login_view(request,year=None,month=None):
    if year is None:
        year = datetime.now().year
    if month is None:
        month = datetime.now().strftime('%B')
        data = create_calendar(year, month)
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
    context = {
        'user': user,
        'katildigi_etkinlikler': katildigi_etkinlikler,
        'katildigi_etkinlik_sayisi': katildigi_etkinlik_sayisi,
        'olusturdugu_etkinlikler': olusturdugu_etkinlikler,
        'olusturdugu_etkinlik_sayisi': olusturdugu_etkinlik_sayisi,
    }
    context.update(data)  # data sözlüğünü context sözlüğüne güncelle
    return render(request, 'profile/my_profile.html', context)


from django.contrib import messages
def custom_logout(request):
    user = request.user
    if user.is_authenticated:
        logout(request)
        messages.info(request, "Çıkış Yapıldı !")
        return redirect("home")
    else:
        return redirect("home")