# ai_assistant/urls.py

from django.urls import path
from . import views

app_name = 'ai_assistant'

urlpatterns = [
    path('', views.ai_dashboard, name='ai_dashboard'),
    path('board/<int:board_pk>/analyze/', views.analyze_board, name='analyze_board'),
    path('generate-description/', views.generate_card_description, name='generate_description'),
    path('card/<int:card_pk>/generate-description/', views.generate_card_description, name='generate_card_description'),
    path('card/<int:card_pk>/next-steps/', views.suggest_next_steps, name='suggest_next_steps'),
    path('board/<int:board_pk>/sprint-report/', views.generate_sprint_report, name='generate_sprint_report'),
    path('code-review/', views.review_code, name='review_code'),
    path('custom-query/', views.custom_ai_query, name='custom_ai_query'),
    path('prompt-templates/', views.prompt_templates, name='prompt_templates'),
    path('prompt-templates/create/', views.create_prompt_template, name='create_prompt_template'),
    path('prompt-templates/<int:template_pk>/edit/', views.edit_prompt_template, name='edit_prompt_template'),
    path('prompt-templates/<int:template_pk>/delete/', views.delete_prompt_template, name='delete_prompt_template'),
    path('prompt-templates/<int:template_pk>/use/', views.use_prompt_template, name='use_prompt_template'),
]