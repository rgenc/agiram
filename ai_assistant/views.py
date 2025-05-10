# ai_assistant/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from boards.models import Board, Card
from .models import AIPromptTemplate, AIAssistantInteraction, AICardSuggestion
from .services import ClaudeService

@login_required
def ai_dashboard(request):
    # Kullanıcının erişimi olan panolar
    owned_boards = Board.objects.filter(owner=request.user)
    member_boards = Board.objects.filter(members=request.user)
    
    # Kullanıcının AI etkileşimleri
    interactions = AIAssistantInteraction.objects.filter(user=request.user).order_by('-created_at')[:10]
    
    context = {
        'owned_boards': owned_boards,
        'member_boards': member_boards,
        'interactions': interactions,
    }
    
    return render(request, 'ai_assistant/dashboard.html', context)

@login_required
def analyze_board(request, board_pk):
    board = get_object_or_404(Board, pk=board_pk)
    
    # Yetki kontrolü
    if request.user != board.owner and request.user not in board.members.all():
        messages.error(request, 'Bu panoyu analiz etme yetkiniz yok.')
        return redirect('boards:dashboard')
    
    claude_service = ClaudeService()
    
    try:
        analysis = claude_service.analyze_board(board, request.user)
        
        context = {
            'board': board,
            'analysis': analysis,
        }
        
        return render(request, 'ai_assistant/board_analysis.html', context)
    
    except Exception as e:
        messages.error(request, f'Pano analizi sırasında bir hata oluştu: {str(e)}')
        return redirect('boards:board_detail', pk=board_pk)

@login_required
def generate_card_description(request, card_pk=None):
    """
    Kart açıklaması oluşturur. card_pk verilirse mevcut kart için,
    verilmezse yeni bir kart için açıklama oluşturur.
    """
    if request.method == 'POST':
        claude_service = ClaudeService()
        card_title = request.POST.get('card_title')
        
        if card_pk:
            card = get_object_or_404(Card, pk=card_pk)
            board = card.list.board
            
            # Yetki kontrolü
            if request.user != board.owner and request.user not in board.members.all():
                messages.error(request, 'Bu kartı güncelleme yetkiniz yok.')
                return redirect('boards:dashboard')
            
            description = claude_service.generate_card_description(card_title, request.user, board, card)
            
            # Kart açıklamasını güncelle
            card.description = description
            card.save()
            
            messages.success(request, 'Kart açıklaması AI tarafından oluşturuldu.')
            return redirect('boards:card_detail', card_pk=card.pk)
        else:
            board_pk = request.POST.get('board_pk')
            board = get_object_or_404(Board, pk=board_pk)
            
            # Yetki kontrolü
            if request.user != board.owner and request.user not in board.members.all():
                messages.error(request, 'Bu panoda kart oluşturma yetkiniz yok.')
                return redirect('boards:dashboard')
            
            description = claude_service.generate_card_description(card_title, request.user, board)
            
            context = {
                'board': board,
                'card_title': card_title,
                'generated_description': description,
            }
            
            return render(request, 'ai_assistant/generated_description.html', context)
    
    # GET isteği için
    if card_pk:
        card = get_object_or_404(Card, pk=card_pk)
        board = card.list.board
        
        # Yetki kontrolü
        if request.user != board.owner and request.user not in board.members.all():
            messages.error(request, 'Bu kartı görüntüleme yetkiniz yok.')
            return redirect('boards:dashboard')
        
        context = {
            'card': card,
            'board': board,
        }
    else:
        board_pk = request.GET.get('board_pk')
        board = get_object_or_404(Board, pk=board_pk)
        
        # Yetki kontrolü
        if request.user != board.owner and request.user not in board.members.all():
            messages.error(request, 'Bu panoda kart oluşturma yetkiniz yok.')
            return redirect('boards:dashboard')
        
        context = {
            'board': board,
        }
    
    return render(request, 'ai_assistant/generate_description.html', context)

@login_required
def suggest_next_steps(request, card_pk):
    card = get_object_or_404(Card, pk=card_pk)
    board = card.list.board
    
    # Yetki kontrolü
    if request.user != board.owner and request.user not in board.members.all():
        messages.error(request, 'Bu kartı görüntüleme yetkiniz yok.')
        return redirect('boards:dashboard')
    
    claude_service = ClaudeService()
    
    try:
        suggestions = claude_service.suggest_next_steps(card, request.user)
        
        context = {
            'card': card,
            'board': board,
            'suggestions': suggestions,
        }
        
        return render(request, 'ai_assistant/next_steps.html', context)
    
    except Exception as e:
        messages.error(request, f'Öneriler oluşturulurken bir hata oluştu: {str(e)}')
        return redirect('boards:card_detail', card_pk=card_pk)

@login_required
def generate_sprint_report(request, board_pk):
    board = get_object_or_404(Board, pk=board_pk)
    
    # Yetki kontrolü
    if request.user != board.owner and request.user not in board.members.all():
        messages.error(request, 'Bu pano için rapor oluşturma yetkiniz yok.')
        return redirect('boards:dashboard')
    
    claude_service = ClaudeService()
    
    try:
        report = claude_service.generate_sprint_report(board, request.user)
        
        context = {
            'board': board,
            'report': report,
        }
        
        return render(request, 'ai_assistant/sprint_report.html', context)
    
    except Exception as e:
        messages.error(request, f'Sprint raporu oluşturulurken bir hata oluştu: {str(e)}')
        return redirect('boards:board_detail', pk=board_pk)

@login_required
def review_code(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        language = request.POST.get('language')
        card_pk = request.POST.get('card_pk')
        
        card = None
        if card_pk:
            card = get_object_or_404(Card, pk=card_pk)
            board = card.list.board
            
            # Yetki kontrolü
            if request.user != board.owner and request.user not in board.members.all():
                messages.error(request, 'Bu kart için kod incelemesi yapma yetkiniz yok.')
                return redirect('boards:dashboard')
        
        claude_service = ClaudeService()
        
        try:
            review = claude_service.review_code(code, language, request.user, card)
            
            context = {
                'code': code,
                'language': language,
                'review': review,
                'card': card,
            }
            
            return render(request, 'ai_assistant/code_review_result.html', context)
        
        except Exception as e:
            messages.error(request, f'Kod incelemesi sırasında bir hata oluştu: {str(e)}')
            if card:
                return redirect('boards:card_detail', card_pk=card.pk)
            else:
                return redirect('ai_assistant:ai_dashboard')
    
    # GET isteği için
    card_pk = request.GET.get('card_pk')
    
    if card_pk:
        card = get_object_or_404(Card, pk=card_pk)
        board = card.list.board
        
        # Yetki kontrolü
        if request.user != board.owner and request.user not in board.members.all():
            messages.error(request, 'Bu kartı görüntüleme yetkiniz yok.')
            return redirect('boards:dashboard')
        
        context = {
            'card': card,
        }
    else:
        context = {}
    
    return render(request, 'ai_assistant/code_review.html', context)

@login_required
def custom_ai_query(request):
    """
    Kullanıcının özel sorguları için AI asistanı
    """
    recent_interactions = AIAssistantInteraction.objects.filter(
        user=request.user, 
        board=None, 
        card=None
    ).order_by('-created_at')[:5]
    
    if request.method == 'POST':
        prompt = request.POST.get('prompt')
        
        if not prompt:
            messages.error(request, 'Lütfen bir soru veya istek girin.')
            return redirect('ai_assistant:custom_ai_query')
        
        claude_service = ClaudeService()
        
        try:
            response = claude_service.get_response(prompt, user=request.user)
            
            context = {
                'prompt': prompt,
                'response': response,
                'recent_interactions': recent_interactions,
            }
            
            return render(request, 'ai_assistant/custom_query.html', context)
        
        except Exception as e:
            messages.error(request, f'AI yanıtı alınırken bir hata oluştu: {str(e)}')
            return redirect('ai_assistant:ai_dashboard')
    
    # GET isteği için
    context = {
        'recent_interactions': recent_interactions,
    }
    
    return render(request, 'ai_assistant/custom_query.html', context)

@login_required
def prompt_templates(request):
    """
    Prompt şablonlarını görüntüler ve yönetir
    """
    templates = AIPromptTemplate.objects.filter(created_by=request.user)
    
    context = {
        'templates': templates,
    }
    
    return render(request, 'ai_assistant/prompt_templates.html', context)

@login_required
def create_prompt_template(request):
    """
    Yeni bir prompt şablonu oluşturur
    """
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        prompt_text = request.POST.get('prompt_text')
        
        if not title or not prompt_text:
            messages.error(request, 'Başlık ve prompt metni gereklidir.')
            return redirect('ai_assistant:create_prompt_template')
        
        template = AIPromptTemplate.objects.create(
            title=title,
            description=description,
            prompt_text=prompt_text,
            created_by=request.user
        )
        
        messages.success(request, 'Prompt şablonu oluşturuldu.')
        return redirect('ai_assistant:prompt_templates')
    
    return render(request, 'ai_assistant/create_prompt_template.html')

@login_required
def edit_prompt_template(request, template_pk):
    """
    Mevcut bir prompt şablonunu düzenler
    """
    template = get_object_or_404(AIPromptTemplate, pk=template_pk)
    
    # Yetki kontrolü
    if request.user != template.created_by:
        messages.error(request, 'Bu şablonu düzenleme yetkiniz yok.')
        return redirect('ai_assistant:prompt_templates')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        prompt_text = request.POST.get('prompt_text')
        
        if not title or not prompt_text:
            messages.error(request, 'Başlık ve prompt metni gereklidir.')
            return redirect('ai_assistant:edit_prompt_template', template_pk=template.pk)
        
        template.title = title
        template.description = description
        template.prompt_text = prompt_text
        template.save()
        
        messages.success(request, 'Prompt şablonu güncellendi.')
        return redirect('ai_assistant:prompt_templates')
    
    context = {
        'template': template,
    }
    
    return render(request, 'ai_assistant/edit_prompt_template.html', context)

@login_required
def delete_prompt_template(request, template_pk):
    """
    Bir prompt şablonunu siler
    """
    template = get_object_or_404(AIPromptTemplate, pk=template_pk)
    
    # Yetki kontrolü
    if request.user != template.created_by:
        messages.error(request, 'Bu şablonu silme yetkiniz yok.')
        return redirect('ai_assistant:prompt_templates')
    
    if request.method == 'POST':
        template.delete()
        messages.success(request, 'Prompt şablonu silindi.')
        return redirect('ai_assistant:prompt_templates')
    
    context = {
        'template': template,
    }
    
    return render(request, 'ai_assistant/delete_prompt_template.html', context)

@login_required
def use_prompt_template(request, template_pk):
    """
    Bir prompt şablonunu kullanarak AI yanıtı alır
    """
    template = get_object_or_404(AIPromptTemplate, pk=template_pk)
    
    # Yetki kontrolü
    if request.user != template.created_by:
        messages.error(request, 'Bu şablonu kullanma yetkiniz yok.')
        return redirect('ai_assistant:prompt_templates')
    
    if request.method == 'POST':
        variables = {}
        
        # Formdan değişkenleri al
        for key, value in request.POST.items():
            if key.startswith('var_'):
                var_name = key[4:]  # 'var_' önekini kaldır
                variables[f"{{{var_name}}}"] = value
        
        # Değişkenleri prompt metnine yerleştir
        prompt_text = template.prompt_text
        for var, value in variables.items():
            prompt_text = prompt_text.replace(var, value)
        
        claude_service = ClaudeService()
        
        try:
            response = claude_service.get_response(prompt_text, user=request.user)
            
            context = {
                'template': template,
                'prompt': prompt_text,
                'response': response,
                'variables': variables,
            }
            
            return render(request, 'ai_assistant/template_response.html', context)
        
        except Exception as e:
            messages.error(request, f'AI yanıtı alınırken bir hata oluştu: {str(e)}')
            return redirect('ai_assistant:prompt_templates')
    
    # Şablondan değişkenleri çıkar
    import re
    variables = re.findall(r'\{([^}]+)\}', template.prompt_text)
    
    context = {
        'template': template,
        'variables': variables,
    }
    
    return render(request, 'ai_assistant/use_template.html', context)