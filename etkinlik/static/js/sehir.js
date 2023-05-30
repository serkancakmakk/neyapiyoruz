document.addEventListener("DOMContentLoaded", function() {
  // DOMContentLoaded olayı tetiklendiğinde çalışacak olan işlevi tanımla
//DOMContentLoaded olayı, HTML belgesinin tamamen yüklendiği ve DOM'un kullanıma hazır hale geldiği anı temsil eder. 
//Bu olay, JavaScript kodunun doğru zamanda çalışmasını ve belge üzerinde işlemler yapmasını sağlar.

  document.getElementById("id_sehir").addEventListener("change", function() {
    // "id_sehir" öğesinin değiştiği zaman çalışacak olan işlevi tanımla

    var sehirId = this.value;
    // Seçilen şehirin değerini al ve sehirId değişkenine ata

    var ilceSelect = document.getElementById("id_ilce");
    // "id_ilce" öğesini seç ve ilceSelect değişkenine ata

    ilceSelect.innerHTML = "";
    // ilceSelect'in içeriğini boşalt

    fetch("/get-ilceler/" + sehirId + "/")
      .then(response => response.json())
      .then(data => {
        // "/get-ilceler/" ile ilgili AJAX isteğini yap
        // Yanıt geldiğinde JSON verisine dönüştür

        data.forEach(ilce => {
          // Her bir ilce öğesi için döngüyü çalıştır

          var option = document.createElement("option");
          // Yeni bir "option" öğesi oluştur

          option.value = ilce.id;
          // "value" özelliğini ilce.id değeriyle ayarla

          option.textContent = ilce.name;
          // Metin içeriğini ilce.name değeriyle ayarla

          ilceSelect.appendChild(option);
          // option öğesini ilceSelect'e ekle
        });
      });
  });
});