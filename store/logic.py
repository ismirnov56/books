from django.db.models import Avg

from store.models import UserBookRelation

'''
Дополнительная логика для расчета среднего рейтинга книги
'''
def set_rating(book):
    rating = UserBookRelation.objects.filter(book=book).aggregate(rating=Avg('rate')).get('rating')
    book.rating = rating
    book.save()

