/* Agiram - AI Destekli Proje Yönetimi
   Ana JavaScript Dosyası */

   document.addEventListener('DOMContentLoaded', function() {
    // Bootstrap Tooltip aktivasyonu
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Otomatik kaybolan uyarılar
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Mobil cihazlarda pano görünümü için dokunmatik desteği
    if (typeof Hammer !== 'undefined') {
        var boardContainer = document.querySelector('.board-container');
        if (boardContainer) {
            var mc = new Hammer(boardContainer);
            mc.on("panleft panright", function(ev) {
                if (ev.type === "panleft") {
                    boardContainer.scrollLeft += 10;
                } else if (ev.type === "panright") {
                    boardContainer.scrollLeft -= 10;
                }
            });
        }
    }

    // Doğum tarihlerinin otomatik biçimlendirilmesi
    var dueDateInputs = document.querySelectorAll('input[type="datetime-local"]');
    dueDateInputs.forEach(function(input) {
        if (!input.value && input.getAttribute('data-default-now') === 'true') {
            var now = new Date();
            var year = now.getFullYear();
            var month = (now.getMonth() + 1).toString().padStart(2, '0');
            var day = now.getDate().toString().padStart(2, '0');
            var hours = now.getHours().toString().padStart(2, '0');
            var minutes = now.getMinutes().toString().padStart(2, '0');
            
            input.value = `${year}-${month}-${day}T${hours}:${minutes}`;
        }
    });

    // Markdown dönüştürme - basit bir versiyon
    var markdownContents = document.querySelectorAll('.markdown-content');
    markdownContents.forEach(function(content) {
        var html = content.innerHTML;
        
        // Başlıklar
        html = html.replace(/^# (.+)$/gm, '<h1>$1</h1>');
        html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>');
        html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>');
        
        // Kalın ve italik
        html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
        html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');
        
        // Listeler
        html = html.replace(/^- (.+)$/gm, '<li>$1</li>');
        html = html.replace(/(<li>.+<\/li>\n?)+/g, '<ul>$&</ul>');
        
        // Kod
        html = html.replace(/`(.+?)`/g, '<code>$1</code>');
        
        content.innerHTML = html;
    });

    // Kart araması
    var searchCardInput = document.getElementById('search-card');
    if (searchCardInput) {
        searchCardInput.addEventListener('input', function() {
            var searchTerm = this.value.toLowerCase();
            var cards = document.querySelectorAll('.card-item');
            
            cards.forEach(function(card) {
                var title = card.querySelector('.card-title').textContent.toLowerCase();
                if (title.includes(searchTerm)) {
                    card.style.display = '';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    }

    // Animasyonlu öncelik etiketleri
    var highPriorityCards = document.querySelectorAll('.priority-high');
    if (highPriorityCards.length > 0) {
        highPriorityCards.forEach(function(card) {
            if (!card.classList.contains('completed')) {
                card.classList.add('pulse-animation');
            }
        });
    }

    // Gecikmiş kartların gösterilmesi
    var overdueCards = document.querySelectorAll('.overdue');
    if (overdueCards.length > 0) {
        overdueCards.forEach(function(card) {
            if (!card.classList.contains('completed')) {
                card.classList.add('border-danger');
            }
        });
    }

    // AI yanıt alanları için otomatik yükseklik ayarlaması
    var aiResponseTextareas = document.querySelectorAll('textarea.auto-resize');
    aiResponseTextareas.forEach(function(textarea) {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
        
        // Sayfa yüklendiğinde de çalıştır
        textarea.dispatchEvent(new Event('input'));
    });

    // Pano filtreleme
    var filterStatusSelect = document.getElementById('filter-status');
    if (filterStatusSelect) {
        filterStatusSelect.addEventListener('change', function() {
            var status = this.value;
            var cards = document.querySelectorAll('.card-item');
            
            cards.forEach(function(card) {
                if (status === 'all') {
                    card.style.display = '';
                } else if (status === 'completed' && card.classList.contains('completed')) {
                    card.style.display = '';
                } else if (status === 'active' && !card.classList.contains('completed')) {
                    card.style.display = '';
                } else if (status === 'overdue' && card.classList.contains('overdue') && !card.classList.contains('completed')) {
                    card.style.display = '';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    }

    // Kart oluşturma/düzenleme formu validation
    var cardForms = document.querySelectorAll('.card-form');
    cardForms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            var titleInput = form.querySelector('[name="title"]');
            if (titleInput && titleInput.value.trim() === '') {
                event.preventDefault();
                titleInput.classList.add('is-invalid');
                
                var invalidFeedback = document.createElement('div');
                invalidFeedback.classList.add('invalid-feedback');
                invalidFeedback.textContent = 'Kart başlığı boş olamaz';
                
                titleInput.parentNode.appendChild(invalidFeedback);
            }
        });
    });

    // AI yanıt yükleme göstergesi
    var aiSubmitButtons = document.querySelectorAll('.ai-submit-btn');
    aiSubmitButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            var form = this.closest('form');
            if (form && form.checkValidity()) {
                this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span> İşleniyor...';
                this.disabled = true;
                form.submit();
            }
        });
    });

    // Sohbet kaydırma
    var chatContainers = document.querySelectorAll('.chat-container');
    chatContainers.forEach(function(container) {
        container.scrollTop = container.scrollHeight;
    });
});