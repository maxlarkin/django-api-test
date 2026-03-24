from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Email
from .serializers import EmailSerializer


class EmailViewSet(viewsets.ModelViewSet):
    """ViewSet для управления письмами."""

    queryset = Email.objects.all()
    serializer_class = EmailSerializer

    def get_queryset(self):
        """Получение писем в папке"""

        queryset = Email.objects.all()
        folder = self.request.query_params.get('folder', None)

        if folder:
            queryset = queryset.filter(folder=folder)

        return queryset

    def create(self, request, *args, **kwargs):
        """Отправка письма"""

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.save(folder='sent', is_read=False)

        return Response(
            EmailSerializer(email).data,
            status=status.HTTP_201_CREATED
        )

    def retrieve(self, request, *args, **kwargs):
        """Открытие письма"""
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
        Перемещение письма в другую папку
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
            'status': '200',
            'message': f'Письмо перемещено в папку "{new_folder}"',
            'email': EmailSerializer(email).data
        })

    def destroy(self, request, *args, **kwargs):
        """Удаление письма из БД."""

        self.get_object()  # Проверка существования
        return super().destroy(request, *args, **kwargs)