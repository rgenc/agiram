# boards/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.http import JsonResponse
from django.urls import reverse_lazy
from .models import Board, List, Card, Comment, Attachment, Activity
from django.contrib.auth.models import User
from django.utils import timezone
import json

@login_required
def dashboard(request):
    owned_boards = Board.objects.filter(owner=request.user)
    member_boards = Board.objects.filter(members=request.user)
    
    context = {
        'owned_boards': owned_boards,
        'member_boards': member_boards,
    }
    
    return render(request, 'boards/dashboard.html', context)

class BoardListView(LoginRequiredMixin, ListView):
    model = Board
    template_name = 'boards/board_list.html'
    context_object_name = 'boards'
    
    def get_queryset(self):
        return Board.objects.filter(owner=self.request.user) | Board.objects.filter(members=self.request.user)

class BoardDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Board
    template_name = 'boards/board_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        board = self.get_object()
        lists = board.lists.all()
        
        context['lists'] = lists
        context['board_members'] = board.members.all()
        
        # Get recent activities
        context['activities'] = Activity.objects.filter(board=board).order_by('-created_at')[:10]
        
        return context
    
    def test_func(self):
        board = self.get_object()
        return self.request.user == board.owner or self.request.user in board.members.all()

class BoardCreateView(LoginRequiredMixin, CreateView):
    model = Board
    fields = ['title', 'description']
    template_name = 'boards/board_form.html'
    
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class BoardUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Board
    fields = ['title', 'description']
    template_name = 'boards/board_form.html'
    
    def test_func(self):
        board = self.get_object()
        return self.request.user == board.owner

class BoardDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Board
    template_name = 'boards/board_confirm_delete.html'
    success_url = reverse_lazy('boards:dashboard')
    
    def test_func(self):
        board = self.get_object()
        return self.request.user == board.owner

@login_required
def add_board_member(request, pk):
    board = get_object_or_404(Board, pk=pk)
    
    if request.user != board.owner:
        messages.error(request, 'Sadece pano sahibi üye ekleyebilir.')
        return redirect('boards:board_detail', pk=pk)
    
    if request.method == 'POST':
        username = request.POST.get('username')
        
        try:
            user = User.objects.get(username=username)
            
            if user == request.user:
                messages.error(request, 'Kendinizi üye olarak ekleyemezsiniz.')
            elif user in board.members.all():
                messages.error(request, f'{username} zaten bu panoda üye.')
            else:
                board.members.add(user)
                messages.success(request, f'{username} panoya üye olarak eklendi.')
        except User.DoesNotExist:
            messages.error(request, f'Kullanıcı adı "{username}" bulunamadı.')
    
    return redirect('boards:board_detail', pk=pk)

@login_required
def remove_board_member(request, board_pk, user_pk):
    board = get_object_or_404(Board, pk=board_pk)
    user = get_object_or_404(User, pk=user_pk)
    
    if request.user != board.owner:
        messages.error(request, 'Sadece pano sahibi üyeleri çıkarabilir.')
        return redirect('boards:board_detail', pk=board_pk)
    
    if user in board.members.all():
        board.members.remove(user)
        messages.success(request, f'{user.username} panodan çıkarıldı.')
    
    return redirect('boards:board_detail', pk=board_pk)

@login_required
def create_list(request, board_pk):
    board = get_object_or_404(Board, pk=board_pk)
    
    if request.user != board.owner and request.user not in board.members.all():
        messages.error(request, 'Bu panoda liste oluşturma yetkiniz yok.')
        return redirect('boards:board_detail', pk=board_pk)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        
        if title:
            position = board.lists.count()
            List.objects.create(title=title, board=board, position=position)
            messages.success(request, 'Liste oluşturuldu.')
        else:
            messages.error(request, 'Liste başlığı boş olamaz.')
    
    return redirect('boards:board_detail', pk=board_pk)

@login_required
def update_list(request, list_pk):
    list_obj = get_object_or_404(List, pk=list_pk)
    board = list_obj.board
    
    if request.user != board.owner and request.user not in board.members.all():
        messages.error(request, 'Bu listeyi güncelleme yetkiniz yok.')
        return redirect('boards:board_detail', pk=board.pk)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        
        if title:
            list_obj.title = title
            list_obj.save()
            messages.success(request, 'Liste güncellendi.')
        else:
            messages.error(request, 'Liste başlığı boş olamaz.')
    
    return redirect('boards:board_detail', pk=board.pk)

@login_required
def delete_list(request, list_pk):
    list_obj = get_object_or_404(List, pk=list_pk)
    board = list_obj.board
    
    if request.user != board.owner and request.user not in board.members.all():
        messages.error(request, 'Bu listeyi silme yetkiniz yok.')
        return redirect('boards:board_detail', pk=board.pk)
    
    if request.method == 'POST':
        list_obj.delete()
        messages.success(request, 'Liste silindi.')
    
    return redirect('boards:board_detail', pk=board.pk)

@login_required
def create_card(request, list_pk):
    list_obj = get_object_or_404(List, pk=list_pk)
    board = list_obj.board
    
    if request.user != board.owner and request.user not in board.members.all():
        messages.error(request, 'Bu listede kart oluşturma yetkiniz yok.')
        return redirect('boards:board_detail', pk=board.pk)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        
        if title:
            position = list_obj.cards.count()
            card = Card.objects.create(
                title=title,
                list=list_obj,
                created_by=request.user,
                position=position
            )
            
            # Aktivite kaydı
            Activity.objects.create(
                board=board,
                user=request.user,
                action='create_card',
                card=card,
                list=list_obj,
                description=f'"{title}" kartını "{list_obj.title}" listesinde oluşturdu.'
            )
            
            messages.success(request, 'Kart oluşturuldu.')
        else:
            messages.error(request, 'Kart başlığı boş olamaz.')
    
    return redirect('boards:board_detail', pk=board.pk)

@login_required
def card_detail(request, card_pk):
    card = get_object_or_404(Card, pk=card_pk)
    board = card.list.board
    
    if request.user != board.owner and request.user not in board.members.all():
        messages.error(request, 'Bu kartı görüntüleme yetkiniz yok.')
        return redirect('boards:dashboard')
    
    comments = card.comments.all()
    attachments = card.attachments.all()
    
    if request.method == 'POST':
        comment_text = request.POST.get('comment_text')
        
        if comment_text:
            comment = Comment.objects.create(
                card=card,
                author=request.user,
                text=comment_text
            )
            
            # Aktivite kaydı
            Activity.objects.create(
                board=board,
                user=request.user,
                action='comment_card',
                card=card,
                description=f'"{card.title}" kartına yorum yaptı.'
            )
            
            messages.success(request, 'Yorum eklendi.')
            return redirect('boards:card_detail', card_pk=card.pk)
    
    context = {
        'card': card,
        'board': board,
        'comments': comments,
        'attachments': attachments,
        'board_members': board.members.all(),
    }
    
    return render(request, 'boards/card_detail.html', context)

@login_required
def update_card(request, card_pk):
    card = get_object_or_404(Card, pk=card_pk)
    board = card.list.board
    
    if request.user != board.owner and request.user not in board.members.all():
        messages.error(request, 'Bu kartı güncelleme yetkiniz yok.')
        return redirect('boards:dashboard')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        due_date_str = request.POST.get('due_date')
        priority = request.POST.get('priority')
        
        card.title = title
        card.description = description
        card.priority = priority
        
        if due_date_str:
            try:
                # Format: YYYY-MM-DDTHH:MM
                card.due_date = timezone.datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M')
            except ValueError:
                messages.error(request, 'Geçersiz tarih formatı.')
        else:
            card.due_date = None
        
        card.save()
        messages.success(request, 'Kart güncellendi.')
        
        return redirect('boards:card_detail', card_pk=card.pk)
    
    context = {
        'card': card,
        'board': board,
    }
    
    return render(request, 'boards/update_card.html', context)

@login_required
def delete_card(request, card_pk):
    card = get_object_or_404(Card, pk=card_pk)
    board = card.list.board
    
    if request.user != board.owner and request.user not in board.members.all():
        messages.error(request, 'Bu kartı silme yetkiniz yok.')
        return redirect('boards:dashboard')
    
    if request.method == 'POST':
        list_id = card.list.id
        card.delete()
        messages.success(request, 'Kart silindi.')
        
        return redirect('boards:board_detail', pk=board.pk)
    
    context = {
        'card': card,
        'board': board,
    }
    
    return render(request, 'boards/card_confirm_delete.html', context)

@login_required
def assign_card(request, card_pk):
    card = get_object_or_404(Card, pk=card_pk)
    board = card.list.board
    
    if request.user != board.owner and request.user not in board.members.all():
        messages.error(request, 'Bu kartı atama yetkiniz yok.')
        return redirect('boards:dashboard')
    
    if request.method == 'POST':
        user_ids = request.POST.getlist('assigned_to')
        
        # Tüm atanmış kullanıcıları temizle
        card.assigned_to.clear()
        
        # Seçilen kullanıcıları ekle
        for user_id in user_ids:
            try:
                user = User.objects.get(pk=user_id)
                if user == board.owner or user in board.members.all():
                    card.assigned_to.add(user)
                    
                    # Aktivite kaydı
                    Activity.objects.create(
                        board=board,
                        user=request.user,
                        action='assign_card',
                        card=card,
                        description=f'"{card.title}" kartını {user.username} kullanıcısına atadı.'
                    )
            except User.DoesNotExist:
                pass
        
        messages.success(request, 'Kart ataması güncellendi.')
        
    return redirect('boards:card_detail', card_pk=card.pk)

@login_required
def toggle_card_complete(request, card_pk):
    card = get_object_or_404(Card, pk=card_pk)
    board = card.list.board
    
    if request.user != board.owner and request.user not in board.members.all():
        messages.error(request, 'Bu kartı güncelleme yetkiniz yok.')
        return redirect('boards:dashboard')
    
    card.is_completed = not card.is_completed
    card.save()
    
    action = 'complete_card' if card.is_completed else 'reopen_card'
    status = 'tamamlandı' if card.is_completed else 'yeniden açıldı'
    
    # Aktivite kaydı
    Activity.objects.create(
        board=board,
        user=request.user,
        action=action,
        card=card,
        description=f'"{card.title}" kartı {status}.'
    )
    
    messages.success(request, f'Kart {status}.')
    
    return redirect('boards:card_detail', card_pk=card.pk)

@login_required
def upload_attachment(request, card_pk):
    card = get_object_or_404(Card, pk=card_pk)
    board = card.list.board
    
    if request.user != board.owner and request.user not in board.members.all():
        messages.error(request, 'Bu karta dosya yükleme yetkiniz yok.')
        return redirect('boards:dashboard')
    
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        Attachment.objects.create(
            card=card,
            file=file,
            uploaded_by=request.user
        )
        
        messages.success(request, 'Dosya yüklendi.')
    
    return redirect('boards:card_detail', card_pk=card.pk)

@login_required
def delete_attachment(request, attachment_pk):
    attachment = get_object_or_404(Attachment, pk=attachment_pk)
    card = attachment.card
    board = card.list.board
    
    if request.user != board.owner and request.user != attachment.uploaded_by:
        messages.error(request, 'Bu dosyayı silme yetkiniz yok.')
        return redirect('boards:dashboard')
    
    if request.method == 'POST':
        attachment.file.delete()
        attachment.delete()
        messages.success(request, 'Dosya silindi.')
    
    return redirect('boards:card_detail', card_pk=card.pk)

@login_required
def update_card_position(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        card_id = data.get('cardId')
        source_list_id = data.get('sourceListId')
        target_list_id = data.get('targetListId')
        new_position = data.get('newPosition')
        
        card = get_object_or_404(Card, pk=card_id)
        board = card.list.board
        
        if request.user != board.owner and request.user not in board.members.all():
            return JsonResponse({'error': 'Yetkiniz yok'}, status=403)
        
        source_list = get_object_or_404(List, pk=source_list_id)
        target_list = get_object_or_404(List, pk=target_list_id)
        
        # Liste değişimi
        if source_list.id != target_list.id:
            old_list_name = card.list.title
            card.list = target_list
            
            # Aktivite kaydı
            Activity.objects.create(
                board=board,
                user=request.user,
                action='move_card',
                card=card,
                list=target_list,
                description=f'"{card.title}" kartını "{old_list_name}" listesinden "{target_list.title}" listesine taşıdı.'
            )
        
        # Pozisyon güncelleme
        card.position = new_position
        card.save()
        
        # Diğer kartların pozisyonlarını güncelle
        cards_to_update = Card.objects.filter(list=target_list).exclude(pk=card_id)
        for c in cards_to_update:
            if c.position >= new_position:
                c.position += 1
                c.save()
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'error': 'Geçersiz istek'}, status=400)

@login_required
def update_list_position(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        list_id = data.get('listId')
        new_position = data.get('newPosition')
        
        list_obj = get_object_or_404(List, pk=list_id)
        board = list_obj.board
        
        if request.user != board.owner and request.user not in board.members.all():
            return JsonResponse({'error': 'Yetkiniz yok'}, status=403)
        
        old_position = list_obj.position
        list_obj.position = new_position
        list_obj.save()
        
        # Diğer listelerin pozisyonlarını güncelle
        lists_to_update = List.objects.filter(board=board).exclude(pk=list_id)
        
        if old_position < new_position:
            for lst in lists_to_update:
                if old_position < lst.position <= new_position:
                    lst.position -= 1
                    lst.save()
        else:
            for lst in lists_to_update:
                if new_position <= lst.position < old_position:
                    lst.position += 1
                    lst.save()
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'error': 'Geçersiz istek'}, status=400)