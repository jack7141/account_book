from django.db import models
from api.bases.users.models import User
from common.behaviors import Timestampable
import copy
from django.core.cache import cache
from functools import lru_cache
from django.core.cache import cache
class SumUp(Timestampable, models.Model):
    class TransactionChoices(models.TextChoices):
        INCOME = ("INCOME", "수입")
        SPENDING = ("SPENDING", "지출")

    _AMOUNT_FUNCS = [
        ('INCOME', [
            ('INCOME_SALARY', '월급 입금'),
            ('INCOME_PIN', '용돈 입금'),
            ('INCOME_CARRY_OVER', '이월 입금'),
            ('INCOME_WITHDRAWAL', '자산 인출 입금'),
            ('INCOME_ETC', '자산 인출 입금'),
        ]),
        ('SPENDING', [
            ('SPENDING_FOOD', '식비 출금'),
            ('SPENDING_TRANSPORTATION', '교통비 출금'),
            ('SPENDING_CLTURE', '문화생활 출금'),
            ('SPENDING_BUEATY', '미용 출금'),
            ('SPENDING_DRESS', '의류 출금'),
            ('SPENDING_ADU', '교육 출금'),
            ('SPENDING_MOBILE', '통신비 출금'),
            ('SPENDING_SAVE', '저축 출금'),
        ])
    ]
    email = models.ForeignKey(User, on_delete=models.CASCADE, help_text="이메일")
    j_name = models.CharField(blank=True, null=True, max_length=35, help_text='적요명')
    transaction = models.CharField(
        max_length=300,
        choices=TransactionChoices.choices,
    )
    trade_type = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.trade_type

    @staticmethod
    def get_trade_types():
        trade_types = SumUp.objects.values_list('transaction', 'trade_type').distinct()
        _AMOUNT_FUNCS_COPY = copy.deepcopy(SumUp._AMOUNT_FUNCS)

        for key, val in trade_types:
            if ('', val) not in dict(SumUp._AMOUNT_FUNCS)[key]:
                dict(_AMOUNT_FUNCS_COPY)[key].append(('', val))

        return _AMOUNT_FUNCS_COPY

