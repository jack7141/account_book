from django.db import models
from api.bases.users.models import User
from common.behaviors import Timestampable
from model_utils import Choices
from collections import defaultdict
from django.db.models.signals import post_save
from django.dispatch import receiver

class Category(models.Model):
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
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="categories")
    tag = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.name

    @staticmethod
    def get_trade_types():
        trade_types = Category.objects.values_list('transaction', 'trade_type').distinct()
        _AMOUNT_FUNCS_COPY = copy.deepcopy(Category._AMOUNT_FUNCS)

        for key, val in trade_types:
            if ('', val) not in dict(Category._AMOUNT_FUNCS)[key]:
                dict(_AMOUNT_FUNCS_COPY)[key].append(('', val))

        return _AMOUNT_FUNCS_COPY

    @staticmethod
    def get_category_choices():
        default_choices = [
            ('식비', '식비'),
            ('생활', '생활'),
            ('교통', '교통'),
            ('쇼핑/뷰티', '쇼핑/뷰티'),
            ('의료/건강', '의료/건강'),
            ('문화/여가', '문화/여가'),
            ('미분류', '미분류'),
        ]
        # user_choices = list(Category.objects.filter(user_id=user_id).values_list("name", "name"))
        # choices = default_choices + user_choices
        return default_choices


class Asset(Timestampable, models.Model):
    id = models.BigAutoField(primary_key=True)
    email = models.ForeignKey(User, on_delete=models.CASCADE, help_text="이메일")
    amount = models.IntegerField(null=False, help_text="금액(KRW)")
    description = models.CharField(help_text="설명", max_length=100, null=True)
    trade_type = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True, help_text="Trade type",
                                   choices=Category.get_trade_types())
    managed = models.BooleanField(default=True, help_text="관리여부")

    def __str__(self):
        return f'{self.email}({self.trade_type} - {self.amount}) - {self.description}'

