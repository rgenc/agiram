# ai_assistant/services.py

import anthropic
from django.conf import settings
from .models import AIAssistantInteraction

class ClaudeService:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = "claude-3-5-sonnet-20240620"
    
    def get_response(self, prompt, user=None, board=None, card=None, max_tokens=2000):
        """
        Claude API kullanarak bir prompt'a yanıt alır
        """
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Claude'un yanıtını al
            response_text = response.content[0].text
            
            # Etkileşimi kaydet
            if user:
                AIAssistantInteraction.objects.create(
                    user=user,
                    board=board,
                    card=card,
                    prompt=prompt,
                    response=response_text
                )
            
            return response_text
        
        except Exception as e:
            return f"Claude API ile iletişim kurarken bir hata oluştu: {str(e)}"
    
    def analyze_board(self, board, user):
        """
        Bir panoyu analiz eder ve önerilerde bulunur
        """
        board_lists = board.lists.all()
        cards_info = []
        
        # Pano verilerini topla
        for lst in board_lists:
            cards = lst.cards.all()
            for card in cards:
                assigned_users = [user.username for user in card.assigned_to.all()]
                cards_info.append({
                    'list': lst.title,
                    'title': card.title,
                    'description': card.description,
                    'assigned_to': assigned_users,
                    'due_date': card.due_date,
                    'is_completed': card.is_completed,
                    'priority': card.priority
                })
        
        # Claude'a gönderilecek prompt oluştur
        prompt = f"""
        Sen bir proje yönetim asistanısın. Aşağıdaki agile pano verileri için analiz yapıp önerilerde bulun:
        
        Pano: {board.title}
        Açıklama: {board.description}
        
        Kartlar:
        {cards_info}
        
        Lütfen şunları yap:
        1. Proje durumunun kısa bir analizini yap
        2. Riskli görünen kartları belirle (gecikmiş veya yakında bitecek yüksek öncelikli kartlar)
        3. İş akışı için optimizasyon önerileri sun
        4. Eksik gibi görünen görevler için öneriler yap
        5. Takıma yardımcı olabilecek 2-3 yeni kart öner
        """
        
        return self.get_response(prompt, user=user, board=board)
    
    def generate_card_description(self, card_title, user, board=None, card=None):
        """
        Bir kart başlığı için detaylı açıklama oluşturur
        """
        prompt = f"""
        Sen bir agile proje yönetimi uzmanısın. Aşağıdaki kart başlığı için detaylı bir kart açıklaması oluştur:
        
        Kart Başlığı: {card_title}
        
        Açıklama şunları içermeli:
        1. Görevin kısa bir özeti
        2. Tamamlanması için gerekli adımlar
        3. Başarı kriterleri
        4. Tahmini efor (saat veya story point olarak)
        5. Gerekli kaynaklar veya bağımlılıklar
        
        Yanıtını markdown formatında ver.
        """
        
        return self.get_response(prompt, user=user, board=board, card=card)
    
    def suggest_next_steps(self, card, user):
        """
        Bir kart için sonraki adımları önerir
        """
        prompt = f"""
        Sen bir agile proje yönetimi uzmanısın. Aşağıdaki kart için sonraki adımları öner:
        
        Kart Başlığı: {card.title}
        Açıklama: {card.description}
        Durum: {"Tamamlandı" if card.is_completed else "Devam Ediyor"}
        Öncelik: {card.priority}
        
        Lütfen aşağıdakileri içeren bir yanıt ver:
        1. Bu görev için 3-5 somut sonraki adım
        2. Her adım için tahmini süre
        3. Olası engeller ve bunları nasıl aşabileceğim
        4. Bu işi daha verimli yapabilmem için ipuçları
        
        Yanıtını markdown formatında ver.
        """
        
        return self.get_response(prompt, user=user, board=card.list.board, card=card)
    
    def generate_sprint_report(self, board, user):
        """
        Bir pano için sprint raporu oluşturur
        """
        board_lists = board.lists.all()
        completed_cards = []
        in_progress_cards = []
        
        # Pano verilerini topla
        for lst in board_lists:
            cards = lst.cards.all()
            for card in cards:
                card_info = {
                    'list': lst.title,
                    'title': card.title,
                    'description': card.description,
                    'assigned_to': [user.username for user in card.assigned_to.all()],
                    'priority': card.priority
                }
                
                if card.is_completed:
                    completed_cards.append(card_info)
                else:
                    in_progress_cards.append(card_info)
        
        # Claude'a gönderilecek prompt oluştur
        prompt = f"""
        Sen bir agile scrum master'sın. Aşağıdaki pano verileri için bir sprint raporu oluştur:
        
        Pano: {board.title}
        Açıklama: {board.description}
        
        Tamamlanan Kartlar:
        {completed_cards}
        
        Devam Eden Kartlar:
        {in_progress_cards}
        
        Lütfen aşağıdakileri içeren profesyonel bir sprint raporu hazırla:
        
        1. Sprint Özeti
        2. Tamamlanan İşler ve Başarılar
        3. Devam Eden İşler
        4. Engeller ve Zorluklar
        5. Sonraki Sprint için Öneriler
        6. Takım Performans Analizi
        
        Raporu markdown formatında hazırla.
        """
        
        return self.get_response(prompt, user=user, board=board, max_tokens=4000)
    
    def review_code(self, code, language, user, card=None):
        """
        Kod incelemesi yapar
        """
        prompt = f"""
        Sen deneyimli bir yazılım geliştiricisin. Aşağıdaki {language} kodunu incele:
        
        ```{language}
        {code}
        ```
        
        Lütfen aşağıdakileri içeren bir kod incelemesi yap:
        
        1. Kodun genel kalitesi ve okunaklılığı
        2. Olası hatalar veya sorunlar
        3. Performans iyileştirmeleri
        4. En iyi uygulamalara uygunluk
        5. Güvenlik sorunları
        6. İyileştirme önerileri
        
        İncelemeyi markdown formatında hazırla.
        """
        
        board = card.list.board if card else None
        
        return self.get_response(prompt, user=user, board=board, card=card)