from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Email
from .serializers import EmailSerializer


class EmailViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления письмами.
    Все эндпоинты публичные — без аутентификации.
    """
    queryset = Email.objects.all()
    serializer_class = EmailSerializer
    # Нет permission_classes — доступ открыт всем

    def get_queryset(self):
        """
        Базовая фильтрация по папке через query-параметр.
        Пример: /api/emails/?folder=inbox
        """
        queryset = Email.objects.all()
        folder = self.request.query_params.get('folder', None)
        
        if folder:
            queryset = queryset.filter(folder=folder)
        
        # Дополнительная фильтрация по email (опционально)
        email = self.request.query_params.get('email', None)
        if email:
            # Поиск писем, где пользователь — отправитель ИЛИ получатель
            queryset = queryset.filter(
                models.Q(sender=email) | models.Q(recipient=email)
            )
        
        return queryset

    def create(self, request, *args, **kwargs):
        """
        📤 ОТПРАВКА ПИСЬМА
        Создаёт одну запись в БД с указанными sender/recipient.
        Для упрощения: письмо сразу попадает в папку 'sent' для отправителя
        и отдельным запросом может быть создано для получателя (опционально).
        
        В тестовом режиме создаём ОДНУ запись с папкой по умолчанию 'inbox' 
        для получателя. Отправитель может фильтровать по своему email.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Письмо создаётся в папке 'inbox' получателя
        # Отправитель видит его, фильтруя по своему email как sender
        email = serializer.save(folder='inbox', is_read=False)
        
        return Response(
            EmailSerializer(email).data, 
            status=status.HTTP_201_CREATED
        )

    def retrieve(self, request, *args, **kwargs):
        """
        👁️ ПРОСМОТР ПИСЬМА
        Автоматически помечает письмо как прочитанное (is_read=True).
        """
        instance = self.get_object()
        
        # Помечаем как прочитанное, если ещё не было
        if not instance.is_read:
            instance.is_read = True
            instance.save(update_fields=['is_read'])
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'])
    def move(self, request, pk=None):
        """
        📁 ПЕРЕМЕЩЕНИЕ ПИСЬМА МЕЖДУ ПАПКАМИ
        PATCH /api/emails/{id}/move/
        Body: {"folder": "archive"}
        """
        email = self.get_object()
        new_folder = request.data.get('folder')
        
        valid_folders = ['inbox', 'sent', 'archive', 'trash']
        if new_folder not in valid_folders:
            return Response(
                {'error': f'Допустимые папки: {valid_folders}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        email.folder = new_folder
        email.save(update_fields=['folder'])
        
        return Response({
            'status': 'success',
            'message': f'Письмо перемещено в папку "{new_folder}"',
            'email': EmailSerializer(email).data
        })

    def destroy(self, request, *args, **kwargs):
        """
        🗑️ УДАЛЕНИЕ ПИСЬМА
        Полное удаление записи из БД.
        """
        email_id = kwargs.get('pk')
        self.get_object()  # Проверка существования
        return super().destroy(request, *args, **kwargs)