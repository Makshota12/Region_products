from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Product, Domain, Criterion, RatingScale, EvaluationSession, AssignedCriterion, EvaluationAnswer, Role, Profile
from .serializers import (ProductSerializer, DomainSerializer, CriterionSerializer, RatingScaleSerializer, 
                          EvaluationSessionSerializer, AssignedCriterionSerializer, AssignedCriterionReadSerializer,
                          EvaluationAnswerSerializer, RoleSerializer, ProfileSerializer, UserSerializer)

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, cm
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from django.http import HttpResponse
import os

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

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class DomainViewSet(viewsets.ModelViewSet):
    queryset = Domain.objects.all()
    serializer_class = DomainSerializer

class CriterionViewSet(viewsets.ModelViewSet):
    queryset = Criterion.objects.all()
    serializer_class = CriterionSerializer

class RatingScaleViewSet(viewsets.ModelViewSet):
    queryset = RatingScale.objects.all()
    serializer_class = RatingScaleSerializer

class EvaluationSessionViewSet(viewsets.ModelViewSet):
    queryset = EvaluationSession.objects.all()
    serializer_class = EvaluationSessionSerializer

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
        
        # === СТРАНИЦА 2: ДЕТАЛЬНАЯ ОЦЕНКА ===
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

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

@api_view(['GET'])
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