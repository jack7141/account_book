from django.db import models
from api.bases.users.models import User
from common.behaviors import Timestampable
from model_utils import Choices

class Asset(Timestampable, models.Model):
    class TransactionChoices(models.TextChoices):
        INCOME = ("INCOME", "수입")
        SPENDING = ("SPENDING", "지출")

    _AMOUNT_FUNCS = [
        ('INCOME_SALARY', '월급 입금'),
        ('INCOME_PIN', '용돈 입금'),
        ('INCOME_CARRY_OVER', '이월 입금'),
        ('INCOME_WITHDRAWAL', '자산 인출 입금'),
        ('INCOME_ETC', '자산 인출 입금'),
        ('SPENDING_FOOD', '식비 출금'),
        ('SPENDING_TRANSPORTATION', '교통비 출금'),
        ('SPENDING_CLTURE', '문화생활 출금'),
        ('SPENDING_BUEATY', '미용 출금'),
        ('SPENDING_DRESS', '의류 출금'),
        ('SPENDING_ADU', '교육 출금'),
        ('SPENDING_MOBILE', '통신비 출금'),
        ('SPENDING_SAVE', '저축 출금'),
    ]
    AMOUNT_FUNC_TYPES = Choices(*_AMOUNT_FUNCS)

    id = models.BigAutoField(primary_key=True)
    email = models.ForeignKey(User, on_delete=models.CASCADE, help_text="이메일")
    amount = models.IntegerField(null=False, help_text="금액(KRW)")
    description = models.CharField(help_text="설명", max_length=100, null=True)
    trade_type = models.CharField(max_length=300, blank=True, null=True, choices=AMOUNT_FUNC_TYPES)
    transaction = models.CharField(
        max_length=10,
        choices=TransactionChoices.choices,
    )

    managed = models.BooleanField(default=True, help_text="관리여부")

    def __str__(self):
        return f'{self.email}({self.transaction} - {self.amount}) - {self.description}'


