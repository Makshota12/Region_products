from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import BasePermission, SAFE_METHODS, IsAuthenticated
from django.contrib.auth.models import User
from .models import Product, Domain, Criterion, RatingScale, EvaluationSession, AssignedCriterion, EvaluationAnswer, Role, Profile
from .serializers import (ProductSerializer, DomainSerializer, CriterionSerializer, RatingScaleSerializer, 
                          EvaluationSessionSerializer, AssignedCriterionSerializer, AssignedCriterionReadSerializer,
                          EvaluationAnswerSerializer, RoleSerializer, ProfileSerializer, UserSerializer)

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, cm
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from django.http import HttpResponse
import os
from io import BytesIO

import matplotlib
matplotlib.use('Agg')  # серверный, неинтерактивный backend
import matplotlib.pyplot as plt
import numpy as np


def _render_radar_chart(domain_scores: dict) -> BytesIO:
    """Лепестковая (радарная) диаграмма по доменам. Возвращает PNG в BytesIO."""
    if not domain_scores:
        return None

    labels = list(domain_scores.keys())
    values = [float(v) if v is not None else 0.0 for v in domain_scores.values()]

    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    values_closed = values + values[:1]
    angles_closed = angles + angles[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.fill(angles_closed, values_closed, color='#667eea', alpha=0.25)
    ax.plot(angles_closed, values_closed, color='#667eea', linewidth=2)
    ax.scatter(angles, values, color='#764ba2', s=40, zorder=3)

    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_xticks(angles)
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylim(0, 10)
    ax.set_yticks([2, 4, 6, 8, 10])
    ax.set_yticklabels(['2', '4', '6', '8', '10'], fontsize=8, color='#888')
    ax.grid(color='#e2e2e2')
    ax.set_title('Оценка по доменам', fontsize=14, fontweight='bold', pad=20, color='#2d3436')

    buf = BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    buf.seek(0)
    return buf


def _render_bar_chart(domain_scores: dict) -> BytesIO:
    """Столбчатая диаграмма по доменам. Возвращает PNG в BytesIO."""
    if not domain_scores:
        return None

    labels = list(domain_scores.keys())
    values = [float(v) if v is not None else 0.0 for v in domain_scores.values()]

    def _color_for(v):
        if v >= 8:
            return '#27ae60'
        if v >= 6:
            return '#3498db'
        if v >= 4:
            return '#f39c12'
        if v >= 2:
            return '#e74c3c'
        return '#c0392b'

    colors = [_color_for(v) for v in values]

    fig, ax = plt.subplots(figsize=(8, 4.5))
    bars = ax.bar(labels, values, color=colors, edgecolor='white', linewidth=1.5)
    ax.set_ylim(0, 10)
    ax.set_ylabel('Оценка (0–10)', fontsize=10, color='#2d3436')
    ax.set_title('Сравнение доменов', fontsize=14, fontweight='bold', color='#2d3436', pad=15)
    ax.grid(axis='y', color='#e2e2e2', linestyle='--', alpha=0.7)
    ax.set_axisbelow(True)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#cccccc')
    ax.spines['bottom'].set_color('#cccccc')

    for bar, value in zip(bars, values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2.0, height + 0.15, f'{value:.2f}',
                ha='center', va='bottom', fontsize=9, fontweight='bold', color='#2d3436')

    plt.xticks(rotation=15, ha='right', fontsize=9)
    buf = BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    buf.seek(0)
    return buf


def _render_gauge_chart(overall_index: float) -> BytesIO:
    """Кольцевая диаграмма-«пончик» общего индекса зрелости."""
    overall_index = max(0.0, min(10.0, float(overall_index or 0.0)))
    remaining = 10.0 - overall_index

    if overall_index >= 8:
        color = '#27ae60'
    elif overall_index >= 6:
        color = '#3498db'
    elif overall_index >= 4:
        color = '#f39c12'
    elif overall_index >= 2:
        color = '#e74c3c'
    else:
        color = '#c0392b'

    fig, ax = plt.subplots(figsize=(4.5, 4.5))
    ax.pie(
        [overall_index, remaining],
        colors=[color, '#ecf0f1'],
        startangle=90,
        counterclock=False,
        wedgeprops=dict(width=0.3, edgecolor='white'),
    )
    ax.text(0, 0.05, f'{overall_index:.2f}', ha='center', va='center',
            fontsize=36, fontweight='bold', color=color)
    ax.text(0, -0.25, 'из 10', ha='center', va='center', fontsize=12, color='#636e72')
    ax.set_title('Общий индекс зрелости', fontsize=13, fontweight='bold', color='#2d3436', pad=15)

    buf = BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    buf.seek(0)
    return buf

# Регистрируем шрифт с поддержкой кириллицы
def register_fonts():
    """Регистрация шрифтов с поддержкой кириллицы"""
    fonts_registered = False
    
    # Пути к шрифтам Windows
    font_paths = [
        ('C:/Windows/Fonts/arial.ttf', 'Arial'),
        ('C:/Windows/Fonts/arialbd.ttf', 'Arial-Bold'),
        ('C:/Windows/Fonts/DejaVuSans.ttf', 'DejaVuSans'),
        ('C:/Windows/Fonts/DejaVuSans-Bold.ttf', 'DejaVuSans-Bold'),
    ]
    
    for font_path, font_name in font_paths:
        if os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont(font_name, font_path))
                fonts_registered = True
            except Exception as e:
                print(f"[WARNING] Не удалось загрузить шрифт {font_name}: {e}")
    
    # Если Arial не найден, пробуем другие варианты
    if not fonts_registered:
        # Пробуем системный шрифт
        try:
            import platform
            if platform.system() == 'Windows':
                pdfmetrics.registerFont(TTFont('Arial', 'C:/Windows/Fonts/arial.ttf'))
        except:
            pass
    
    return fonts_registered

# Регистрируем шрифты при загрузке модуля
register_fonts()

# =====================================================================
# РОЛЕВАЯ МОДЕЛЬ ДОСТУПА
# ---------------------------------------------------------------------
# В системе четыре роли (см. core.models.Role):
#   • admin    — Администратор системы:  все действия (CRUD по всему).
#   • expert   — Эксперт/Аудитор:        проводит оценки, не правит каталог.
#   • owner    — Владелец продукта:      управляет продуктами + оценивает.
#   • observer — Наблюдатель:            только просмотр (read-only везде).
#
# Сводная матрица доступа (W = write, R = read, — = запрет):
#
#   Сущность                     admin  expert  owner  observer
#   --------------------------   -----  ------  -----  --------
#   Каталог: Domain, Criterion,
#   RatingScale, AssignedCrit.    W      R       R      R
#   Product (продукты)            W      R       W      R
#   EvaluationSession             W      W       W      R
#   EvaluationAnswer              W      W       W      R
#   Role / Profile / User         W      —       —      —
#
# Все ViewSets ниже привязаны к семантичным пермишенам.
# =====================================================================

ROLE_ADMIN = 'admin'
ROLE_EXPERT = 'expert'
ROLE_OWNER = 'owner'
ROLE_OBSERVER = 'observer'


def _resolve_role(user):
    """Возвращает строковое имя роли пользователя или None.

    Суперпользователи Django и пользователи с is_staff приравниваются к admin
    (нужно для доступа админа Django к API без явной роли в Profile).
    """
    if not user or not user.is_authenticated:
        return None
    if user.is_staff or user.is_superuser:
        return ROLE_ADMIN
    profile = getattr(user, 'profile', None)
    role = getattr(profile, 'role', None) if profile else None
    return role.name if role else None


class IsAdminRole(BasePermission):
    """Только администратор системы."""

    def has_permission(self, request, view):
        return _resolve_role(request.user) == ROLE_ADMIN


class CatalogPermission(BasePermission):
    """Каталог (домены, критерии, шкалы, привязки критериев).

    Чтение — для всех аутентифицированных,
    запись — только администратор.
    """

    def has_permission(self, request, view):
        role = _resolve_role(request.user)
        if role is None:
            return False
        if request.method in SAFE_METHODS:
            return True
        return role == ROLE_ADMIN


class ProductPermission(BasePermission):
    """Продукты.

    Чтение — для всех аутентифицированных,
    запись — администратор или владелец продукта.
    """

    def has_permission(self, request, view):
        role = _resolve_role(request.user)
        if role is None:
            return False
        if request.method in SAFE_METHODS:
            return True
        return role in {ROLE_ADMIN, ROLE_OWNER}


class EvaluationPermission(BasePermission):
    """Сессии оценки и ответы.

    Чтение — для всех аутентифицированных,
    запись — администратор, эксперт или владелец продукта.
    Наблюдатель (observer) может только читать.
    """

    def has_permission(self, request, view):
        role = _resolve_role(request.user)
        if role is None:
            return False
        if request.method in SAFE_METHODS:
            return True
        return role in {ROLE_ADMIN, ROLE_EXPERT, ROLE_OWNER}


# --- Обратная совместимость со старыми именами классов (если где-то импортируются) ---
IsAdminRoleOrReadOnly = CatalogPermission
IsEvaluatorRoleOrReadOnly = EvaluationPermission


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [ProductPermission]

class DomainViewSet(viewsets.ModelViewSet):
    queryset = Domain.objects.all()
    serializer_class = DomainSerializer
    permission_classes = [CatalogPermission]

class CriterionViewSet(viewsets.ModelViewSet):
    queryset = Criterion.objects.all()
    serializer_class = CriterionSerializer
    permission_classes = [CatalogPermission]

class RatingScaleViewSet(viewsets.ModelViewSet):
    queryset = RatingScale.objects.all()
    serializer_class = RatingScaleSerializer
    permission_classes = [CatalogPermission]

class EvaluationSessionViewSet(viewsets.ModelViewSet):
    queryset = EvaluationSession.objects.all()
    serializer_class = EvaluationSessionSerializer
    permission_classes = [EvaluationPermission]

    def create(self, request, *args, **kwargs):
        """
        Переопределяем create для ручного создания критериев
        """
        from django.db import transaction
        
        # Создаем сессию
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        with transaction.atomic():
            # Сохраняем сессию
            self.perform_create(serializer)
            session = serializer.instance
            
            # Создаем критерии вручную
            criteria = Criterion.objects.all()
            created_count = 0
            
            for criterion in criteria:
                _, was_created = AssignedCriterion.objects.get_or_create(
                    evaluation_session=session,
                    criterion=criterion,
                    defaults={
                        'assigned_to': session.created_by,
                        'is_verified': False
                    }
                )
                if was_created:
                    created_count += 1
            
            print(f"[INFO] Создано {created_count} критериев для сессии {session.id}")
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        # Для безопасности фиксируем автора сессии текущим пользователем
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['get'])
    def get_overall_maturity_index(self, request, pk=None):
        session = self.get_object()
        overall_index = session.get_overall_maturity_index()
        
        # Отладка - смотрим сколько ответов есть
        answers_count = EvaluationAnswer.objects.filter(
            assigned_criterion__evaluation_session=session
        ).count()
        
        print(f"[DEBUG] Session {session.id}: answers={answers_count}, overall_index={overall_index}")
        
        return Response({
            'overall_index': overall_index,
            'answers_count': answers_count
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def get_domain_scores(self, request, pk=None):
        session = self.get_object()
        domain_scores = {}
        
        for domain in Domain.objects.all():
            score = session.get_domain_score(domain.id)
            domain_scores[domain.name] = score
            print(f"[DEBUG] Domain '{domain.name}': score={score}")
            
        return Response({'domain_scores': domain_scores}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def generate_maturity_passport(self, request, pk=None):
        """Генерация паспорта зрелости продукта в PDF (на русском языке)"""
        session = self.get_object()
        response = HttpResponse(content_type='application/pdf')
        
        # Безопасное имя файла (латиница)
        safe_name = f"passport_session_{session.id}"
        response['Content-Disposition'] = f'attachment; filename="{safe_name}.pdf"'

        p = canvas.Canvas(response, pagesize=A4)
        width, height = A4
        
        # Определяем шрифты (Arial для кириллицы)
        font_regular = 'Arial'
        font_bold = 'Arial-Bold'
        
        # Проверяем доступность шрифтов
        try:
            p.setFont(font_bold, 12)
        except:
            font_regular = 'Helvetica'
            font_bold = 'Helvetica-Bold'
        
        # Цвета
        primary_color = HexColor('#667eea')
        secondary_color = HexColor('#764ba2')
        text_color = HexColor('#2d3436')
        success_color = HexColor('#27ae60')
        
        # === СТРАНИЦА 1: ТИТУЛЬНАЯ ===
        
        # Заголовок
        p.setFillColor(primary_color)
        p.setFont(font_bold, 28)
        p.drawCentredString(width/2, height - 2*cm, "ПАСПОРТ ЗРЕЛОСТИ")
        p.setFont(font_bold, 24)
        p.drawCentredString(width/2, height - 3*cm, "ЦИФРОВОГО ПРОДУКТА")
        
        # Линия-разделитель
        p.setStrokeColor(primary_color)
        p.setLineWidth(3)
        p.line(2*cm, height - 3.5*cm, width - 2*cm, height - 3.5*cm)
        
        # Информация о продукте
        p.setFillColor(text_color)
        p.setFont(font_bold, 16)
        p.drawString(2*cm, height - 5*cm, "Продукт:")
        p.setFont(font_regular, 14)
        p.drawString(2*cm, height - 5.7*cm, str(session.product.name))
        
        if session.product.description:
            p.setFont(font_regular, 11)
            # Обрезаем длинное описание
            desc = str(session.product.description)[:200]
            if len(session.product.description) > 200:
                desc += "..."
            p.drawString(2*cm, height - 6.4*cm, desc)
        
        p.setFont(font_bold, 14)
        p.drawString(2*cm, height - 7.5*cm, f"Владелец: {session.product.department_owner}")
        p.drawString(2*cm, height - 8.2*cm, f"Дата оценки: {session.start_date.strftime('%d.%m.%Y') if session.start_date else '-'}")
        p.drawString(2*cm, height - 8.9*cm, f"ID сессии: {session.id}")
        
        # === БЛОК: ОБЩИЙ ИНДЕКС ЗРЕЛОСТИ ===
        overall_index = session.get_overall_maturity_index()
        
        # Фон блока
        p.setFillColor(HexColor('#f8f9fa'))
        p.roundRect(2*cm, height - 13*cm, width - 4*cm, 3.5*cm, 10, fill=1, stroke=0)
        
        # Определяем уровень зрелости
        if overall_index >= 8:
            level = "Превосходный"
            level_color = HexColor('#27ae60')
        elif overall_index >= 6:
            level = "Высокий"
            level_color = HexColor('#3498db')
        elif overall_index >= 4:
            level = "Средний"
            level_color = HexColor('#f39c12')
        elif overall_index >= 2:
            level = "Низкий"
            level_color = HexColor('#e74c3c')
        else:
            level = "Критический"
            level_color = HexColor('#c0392b')
        
        p.setFillColor(primary_color)
        p.setFont(font_bold, 18)
        p.drawCentredString(width/2, height - 10*cm, "ОБЩИЙ ИНДЕКС ЗРЕЛОСТИ")
        
        p.setFillColor(level_color)
        p.setFont(font_bold, 48)
        p.drawCentredString(width/2, height - 11.5*cm, f"{overall_index:.2f}")
        
        p.setFont(font_bold, 16)
        p.drawCentredString(width/2, height - 12.5*cm, f"Уровень: {level}")
        
        # === БЛОК: ОЦЕНКИ ПО ДОМЕНАМ ===
        p.setFillColor(text_color)
        p.setFont(font_bold, 16)
        p.drawString(2*cm, height - 15*cm, "ОЦЕНКИ ПО ДОМЕНАМ:")
        
        y_pos = height - 16*cm
        domains = Domain.objects.all()
        
        for domain in domains:
            domain_score = session.get_domain_score(domain.id)
            
            # Название домена
            p.setFont(font_regular, 12)
            p.setFillColor(text_color)
            p.drawString(2*cm, y_pos, f"{domain.name}")
            
            # Оценка
            if domain_score >= 6:
                score_color = success_color
            elif domain_score >= 4:
                score_color = HexColor('#f39c12')
            else:
                score_color = HexColor('#e74c3c')
            
            p.setFillColor(score_color)
            p.setFont(font_bold, 12)
            p.drawString(width - 4*cm, y_pos, f"{domain_score:.2f} / 10")
            
            # Прогресс-бар
            bar_width = 8*cm
            bar_x = 7*cm
            p.setStrokeColor(HexColor('#e9ecef'))
            p.setFillColor(HexColor('#e9ecef'))
            p.rect(bar_x, y_pos - 0.1*cm, bar_width, 0.4*cm, fill=1, stroke=0)
            
            p.setFillColor(score_color)
            filled_width = (domain_score / 10) * bar_width
            p.rect(bar_x, y_pos - 0.1*cm, filled_width, 0.4*cm, fill=1, stroke=0)
            
            y_pos -= 1.2*cm
        
        # === СТРАНИЦА 2: ВИЗУАЛИЗАЦИЯ ОЦЕНОК (ГРАФИКИ) ===
        p.showPage()

        p.setFillColor(primary_color)
        p.setFont(font_bold, 20)
        p.drawCentredString(width / 2, height - 2 * cm, "ВИЗУАЛИЗАЦИЯ ОЦЕНОК")

        p.setStrokeColor(primary_color)
        p.setLineWidth(2)
        p.line(2 * cm, height - 2.5 * cm, width - 2 * cm, height - 2.5 * cm)

        # Собираем оценки по доменам для графиков
        domain_scores_map = {}
        for domain in domains:
            score = session.get_domain_score(domain.id)
            if score is not None:
                domain_scores_map[domain.name] = score

        try:
            # Кольцевая диаграмма общего индекса (правый верх)
            gauge_buf = _render_gauge_chart(overall_index)
            if gauge_buf is not None:
                p.drawImage(
                    ImageReader(gauge_buf),
                    width - 9 * cm, height - 11 * cm,
                    width=8 * cm, height=8 * cm,
                    preserveAspectRatio=True, mask='auto'
                )

            # Радарная диаграмма (левый верх)
            if domain_scores_map:
                radar_buf = _render_radar_chart(domain_scores_map)
                if radar_buf is not None:
                    p.drawImage(
                        ImageReader(radar_buf),
                        1 * cm, height - 11 * cm,
                        width=8 * cm, height=8 * cm,
                        preserveAspectRatio=True, mask='auto'
                    )

            # Столбчатая диаграмма по доменам (нижняя половина страницы)
            if domain_scores_map:
                bar_buf = _render_bar_chart(domain_scores_map)
                if bar_buf is not None:
                    p.drawImage(
                        ImageReader(bar_buf),
                        1.5 * cm, 2.5 * cm,
                        width=width - 3 * cm, height=12 * cm,
                        preserveAspectRatio=True, mask='auto'
                    )
        except Exception as chart_error:
            # Если matplotlib что-то сломал — не валим весь PDF
            p.setFillColor(HexColor('#e74c3c'))
            p.setFont(font_regular, 11)
            p.drawCentredString(width / 2, height / 2,
                                f"Не удалось построить графики: {chart_error}")

        # === СТРАНИЦА 3: ДЕТАЛЬНАЯ ОЦЕНКА ===
        p.showPage()

        p.setFillColor(primary_color)
        p.setFont(font_bold, 20)
        p.drawCentredString(width/2, height - 2*cm, "ДЕТАЛЬНАЯ ОЦЕНКА ПО КРИТЕРИЯМ")
        
        # Линия
        p.setStrokeColor(primary_color)
        p.setLineWidth(2)
        p.line(2*cm, height - 2.5*cm, width - 2*cm, height - 2.5*cm)
        
        y_pos = height - 3.5*cm
        
        # Группируем критерии по доменам
        for domain in domains:
            # Заголовок домена
            p.setFillColor(secondary_color)
            p.setFont(font_bold, 14)
            p.drawString(2*cm, y_pos, f"{domain.name}")
            y_pos -= 0.8*cm
            
            # Критерии домена
            criteria_in_domain = session.assigned_criteria.filter(
                criterion__domain=domain
            ).select_related('criterion')
            
            for ac in criteria_in_domain:
                # Проверяем место на странице
                if y_pos < 3*cm:
                    p.showPage()
                    y_pos = height - 2*cm
                
                # Название критерия
                p.setFillColor(text_color)
                p.setFont(font_regular, 11)
                criterion_name = str(ac.criterion.name)[:50]
                p.drawString(2.5*cm, y_pos, f"• {criterion_name}")
                
                # Оценка
                try:
                    answer = ac.answer
                    score = answer.score_value if answer.score_value else "-"
                    comment = answer.comment if answer.comment else ""
                    
                    if answer.score_value:
                        if answer.score_value >= 7:
                            p.setFillColor(success_color)
                        elif answer.score_value >= 4:
                            p.setFillColor(HexColor('#f39c12'))
                        else:
                            p.setFillColor(HexColor('#e74c3c'))
                    else:
                        p.setFillColor(text_color)
                    
                    p.setFont(font_bold, 11)
                    p.drawString(width - 3*cm, y_pos, f"{score}")
                    
                    # Комментарий (если есть)
                    if comment:
                        p.setFillColor(HexColor('#636e72'))
                        p.setFont(font_regular, 9)
                        comment_short = comment[:80] + "..." if len(comment) > 80 else comment
                        y_pos -= 0.5*cm
                        p.drawString(3*cm, y_pos, comment_short)
                        
                except Exception:
                    p.setFillColor(HexColor('#95a5a6'))
                    p.setFont(font_regular, 11)
                    p.drawString(width - 3*cm, y_pos, "-")
                
                y_pos -= 0.8*cm
            
            y_pos -= 0.5*cm  # Отступ между доменами
        
        # === ФУТЕР ===
        p.setFillColor(HexColor('#95a5a6'))
        p.setFont(font_regular, 9)
        p.drawCentredString(width/2, 1.5*cm, "Система оценки зрелости цифровых продуктов региона")
        p.drawCentredString(width/2, 1*cm, f"Документ сформирован автоматически")
        
        p.save()
        return response


class AssignedCriterionViewSet(viewsets.ModelViewSet):
    queryset = AssignedCriterion.objects.select_related('criterion', 'criterion__domain').prefetch_related('answer')
    permission_classes = [CatalogPermission]
    
    def get_serializer_class(self):
        # Используем разные сериализаторы для чтения и записи
        if self.action in ['list', 'retrieve']:
            return AssignedCriterionReadSerializer
        return AssignedCriterionSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # Фильтрация по evaluation_session
        evaluation_session = self.request.query_params.get('evaluation_session', None)
        if evaluation_session is not None:
            queryset = queryset.filter(evaluation_session=evaluation_session)
        return queryset.order_by('criterion__domain__name', 'criterion__name')


class EvaluationAnswerViewSet(viewsets.ModelViewSet):
    queryset = EvaluationAnswer.objects.all()
    serializer_class = EvaluationAnswerSerializer
    permission_classes = [EvaluationPermission]

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAdminRole]

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAdminRole]

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminRole]

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generate_portfolio_report(request):
    """Генерация сводного отчета по портфелю продуктов (на русском языке)"""
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="portfolio_report.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    
    # Шрифты
    font_regular = 'Arial'
    font_bold = 'Arial-Bold'
    try:
        p.setFont(font_bold, 12)
    except:
        font_regular = 'Helvetica'
        font_bold = 'Helvetica-Bold'
    
    # Цвета
    primary_color = HexColor('#667eea')
    text_color = HexColor('#2d3436')
    success_color = HexColor('#27ae60')
    
    # === ЗАГОЛОВОК ===
    p.setFillColor(primary_color)
    p.setFont(font_bold, 24)
    p.drawCentredString(width/2, height - 2*cm, "СВОДНЫЙ ОТЧЕТ")
    p.setFont(font_bold, 18)
    p.drawCentredString(width/2, height - 3*cm, "ПО ПОРТФЕЛЮ ЦИФРОВЫХ ПРОДУКТОВ")
    
    # Линия
    p.setStrokeColor(primary_color)
    p.setLineWidth(2)
    p.line(2*cm, height - 3.5*cm, width - 2*cm, height - 3.5*cm)
    
    y_pos = height - 5*cm
    
    products = Product.objects.filter(is_archived=False)
    
    for product in products:
        # Проверяем место на странице
        if y_pos < 5*cm:
            p.showPage()
            y_pos = height - 2*cm
        
        # Фон карточки продукта
        p.setFillColor(HexColor('#f8f9fa'))
        p.roundRect(2*cm, y_pos - 3*cm, width - 4*cm, 3.5*cm, 8, fill=1, stroke=0)
        
        # Название продукта
        p.setFillColor(primary_color)
        p.setFont(font_bold, 14)
        p.drawString(2.5*cm, y_pos, str(product.name)[:40])
        
        # Владелец
        p.setFillColor(text_color)
        p.setFont(font_regular, 10)
        p.drawString(2.5*cm, y_pos - 0.6*cm, f"Владелец: {product.department_owner}")
        
        # Получаем последнюю завершенную сессию
        sessions = EvaluationSession.objects.filter(
            product=product, 
            status='completed'
        ).order_by('-start_date')
        
        if sessions.exists():
            latest_session = sessions.first()
            overall_index = latest_session.get_overall_maturity_index()
            
            # Определяем цвет индекса
            if overall_index >= 6:
                index_color = success_color
            elif overall_index >= 4:
                index_color = HexColor('#f39c12')
            else:
                index_color = HexColor('#e74c3c')
            
            # Индекс зрелости
            p.setFillColor(index_color)
            p.setFont(font_bold, 24)
            p.drawString(width - 5*cm, y_pos - 0.3*cm, f"{overall_index:.1f}")
            
            p.setFillColor(text_color)
            p.setFont(font_regular, 9)
            p.drawString(width - 5*cm, y_pos - 1*cm, "из 10")
            
            # Дата оценки
            p.setFont(font_regular, 9)
            date_str = latest_session.start_date.strftime('%d.%m.%Y') if latest_session.start_date else '-'
            p.drawString(2.5*cm, y_pos - 1.2*cm, f"Дата оценки: {date_str}")
            
            # Оценки по доменам (компактно)
            p.setFont(font_regular, 9)
            y_domain = y_pos - 2*cm
            for domain in Domain.objects.all()[:4]:  # Максимум 4 домена
                domain_score = latest_session.get_domain_score(domain.id)
                domain_name = str(domain.name)[:20]
                p.drawString(2.5*cm, y_domain, f"{domain_name}: {domain_score:.1f}")
                y_domain -= 0.4*cm
        else:
            # Нет оценок
            p.setFillColor(HexColor('#95a5a6'))
            p.setFont(font_regular, 11)
            p.drawString(width - 6*cm, y_pos - 0.5*cm, "Нет оценок")
        
        y_pos -= 4.5*cm
    
    # Статистика
    p.showPage()
    p.setFillColor(primary_color)
    p.setFont(font_bold, 20)
    p.drawCentredString(width/2, height - 2*cm, "СТАТИСТИКА ПОРТФЕЛЯ")
    
    # Общее количество
    total_products = products.count()
    evaluated = EvaluationSession.objects.filter(status='completed').values('product').distinct().count()
    
    p.setFillColor(text_color)
    p.setFont(font_bold, 14)
    y_pos = height - 4*cm
    
    p.drawString(2*cm, y_pos, f"Всего продуктов: {total_products}")
    y_pos -= 1*cm
    p.drawString(2*cm, y_pos, f"Оценено продуктов: {evaluated}")
    y_pos -= 1*cm
    p.drawString(2*cm, y_pos, f"Ожидают оценки: {total_products - evaluated}")
    
    # Футер
    p.setFillColor(HexColor('#95a5a6'))
    p.setFont(font_regular, 9)
    p.drawCentredString(width/2, 1.5*cm, "Система оценки зрелости цифровых продуктов региона")
    
    p.save()
    return response