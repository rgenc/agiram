# Agiram - AI Destekli Agile Proje Yönetim Uygulaması

Agiram, Trello benzeri ancak Claude API entegrasyonu ile yapay zeka destekli olarak geliştirilen bir Agile proje yönetim uygulamasıdır. Python ve Django framework kullanılarak geliştirilmiş, responsive tasarıma sahip ve Bootstrap ile şık bir kullanıcı arayüzü sunmaktadır.

## Özellikler

- **Pano Yönetimi**: Kullanıcılar projeler için panolar oluşturabilir, düzenleyebilir ve silebilir
- **Liste ve Kart Sistemi**: Sürükle-bırak arayüzü ile listeler ve kartlar kolayca düzenlenebilir
- **AI Desteği**: Claude API entegrasyonu ile proje yönetiminde yapay zeka desteği
  - Pano analizi ve öneriler
  - Kart açıklamalarının otomatik oluşturulması
  - Sprint raporları oluşturma
  - Kod incelemesi
  - Özel AI sorguları
- **Kullanıcı Yönetimi**: Kayıt, giriş, profil yönetimi
- **Takım İşbirliği**: Panolara üye ekleyerek birlikte çalışma imkanı
- **Aktivite Takibi**: Panolardaki tüm değişiklikler kaydedilir ve görüntülenebilir
- **Görev Atamaları**: Kartlara kullanıcı atanabilir
- **Dosya Ekleri**: Kartlara dosya ekleyebilme
- **Yorumlar**: Kartlara yorum yapabilme
- **Responsive Tasarım**: Mobil cihazlarla uyumlu arayüz

## Teknolojiler

- **Backend**: Python, Django
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Veritabanı**: SQLite (Geliştirme), PostgreSQL (Üretim için önerilen)
- **AI Entegrasyon**: Anthropic Claude API
- **Dosya Yönetimi**: Django Storage
- **Kullanıcı Yetkilendirme**: Django Authentication

## Kurulum

### Gereksinimler

- Python 3.8+
- pip
- virtualenv (önerilen)

### Adımlar

1. **Projeyi Klonlayın**:
   ```bash
   git clone https://github.com/kullaniciadi/agiram.git
   cd agiram
   ```

2. **Sanal Ortam Oluşturun ve Etkinleştirin**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # veya Windows için:
   # venv\Scripts\activate
   ```

3. **Gereksinimleri Yükleyin**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Ortam Değişkenlerini Ayarlayın**:
   Proje kök dizininde `.env` dosyası oluşturun:
   ```
   SECRET_KEY=your_secret_key
   DEBUG=True
   ANTHROPIC_API_KEY=your_anthropic_api_key
   DATABASE_URL=sqlite:///db.sqlite3
   ```

5. **Veritabanını Hazırlayın**:
   ```bash
   python manage.py migrate
   ```

6. **Bir Superuser Oluşturun**:
   ```bash
   python manage.py createsuperuser
   ```

7. **Statik Dosyaları Toplayın**:
   ```bash
   python manage.py collectstatic
   ```

8. **Sunucuyu Başlatın**:
   ```bash
   python manage.py runserver
   ```

9. Tarayıcınızda `http://127.0.0.1:8000` adresine giderek uygulamayı kullanmaya başlayabilirsiniz.

## Claude API Entegrasyonu

Agiram'ın AI özellikleri Claude API ile çalışmaktadır. Bu özellikleri kullanabilmek için:

1. Anthropic'ten bir API anahtarı almanız gerekiyor: [https://anthropic.com](https://anthropic.com)
2. API anahtarınızı `.env` dosyasında `ANTHROPIC_API_KEY` olarak tanımlayın
3. Uygulama otomatik olarak AI özelliklerini etkinleştirecektir

## Üretim Ortamı İçin Öneriler

- **Veritabanı**: PostgreSQL kullanmanız önerilir
- **Web Sunucusu**: Gunicorn + Nginx kombinasyonu
- **Statik Dosyalar**: Whitenoise veya AWS S3 / DigitalOcean Spaces
- **Ortam**: Docker konteynerlerinde çalıştırmak kolaylık sağlar

## Katkıda Bulunma

1. Bu repoyu fork edin
2. Yeni bir özellik dalı oluşturun (`git checkout -b ozellik/yeniozelllik`)
3. Değişikliklerinizi commit edin (`git commit -am 'Yeni özellik: Açıklama'`)
4. Dalınıza push yapın (`git push origin ozellik/yeniozellik`)
5. Bir Pull Request oluşturun

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakın.

## İletişim

Sorular, öneriler veya geribildirimler için lütfen bir issue açın veya iletisim@agiram.com adresine e-posta gönderin.