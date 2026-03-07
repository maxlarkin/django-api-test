from django.db import models


class Email(models.Model):
    FOLDER_CHOICES = [
        ('inbox', 'Входящие'),
        ('sent', 'Отправленные'),
        ('archive', 'Архив'),
        ('trash', 'Корзина'),
    ]

    # Простые строковые поля вместо ForeignKey на User
    sender = models.CharField(max_length=255, db_index=True)
    recipient = models.CharField(max_length=255, db_index=True)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    folder = models.CharField(
        max_length=20,
        choices=FOLDER_CHOICES,
        default='inbox'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Письмо'
        verbose_name_plural = 'Письма'

    def __str__(self):
        return f"{self.subject} ({self.sender} → {self.recipient})"
