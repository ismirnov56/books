from django.db.models import Count, Case, When, F

from store.models import Book, UserBookRelation


def get_books_with_annotate():
    """
    Делаем запрос к Book и делаемвозвращаем queryset
    с дополнительной аннотацией:
    - количество лайков
    - цена с учетом скидки
    - имя владельца книги
    """
    return Book.objects.all().annotate(
        count_likes=Count(Case(When(userbookrelation__like=True, then=1))),
        price_with_discount=F('price') - F('discount'),
        owner_name=F('owner__username')
    ).prefetch_related('readers').order_by('id')


def get_user_book_relation():
    """
    Делаем запрос к UserBookRelation и возвращаем queryset
    """
    return UserBookRelation.objects.all()
