from django.db.models import Count, Case, When, F
from django.test import TestCase
from django.contrib.auth.models import User

from store.models import Book, UserBookRelation
from store.serializers import BooksSerializer


class BookSerializerTestCase(TestCase):
    """
    Тестируем сериализатор для книг
    """
    def test_ok(self):
        user1 = User.objects.create(username='test_user1', first_name='Ivan', last_name='Ivanov')
        user2 = User.objects.create(username='test_user2', first_name='Ivan', last_name='Sidorov')
        user3 = User.objects.create(username='test_user3', first_name='Ivan', last_name='Boboka')


        book_1 = Book.objects.create(name='Test book 1', price=25,
                                          author_name='Author 4', discount=10, owner=user1)
        book_2 = Book.objects.create(name='Test book 2', price=55,
                                          author_name='Author 1')

        UserBookRelation.objects.create(user=user1, book=book_1, like=True, rate=5)
        UserBookRelation.objects.create(user=user2, book=book_1, like=True, rate=5)
        UserBookRelation.objects.create(user=user3, book=book_1, like=True, rate=4)

        UserBookRelation.objects.create(user=user1, book=book_2, like=True, rate=3)
        UserBookRelation.objects.create(user=user2, book=book_2, like=True, rate=4)
        user_book_3 = UserBookRelation.objects.create(user=user3, book=book_2, like=False)
        user_book_3.rate = 4
        user_book_3.save()

        books = Book.objects.all().annotate(
            count_likes=Count(Case(When(userbookrelation__like=True, then=1))),
            price_with_discount=F('price') - F('discount'),
            owner_name=F('owner__username')
        ).prefetch_related('readers').order_by('id')
        data = BooksSerializer(books, many=True).data
        expected_data = [
            {
                'id': book_1.id,
                'name': 'Test book 1',
                'price': '25.00',
                'author_name': 'Author 4',
                'owner_name': 'test_user1',
                'price_with_discount': '15.00',
                'count_likes': 3,
                'rating': '4.7',
                'readers': [
                    {
                        'first_name': 'Ivan',
                        'last_name': 'Ivanov'
                    },
                    {
                        'first_name': 'Ivan',
                        'last_name':'Sidorov'
                    },
                    {
                        'first_name': 'Ivan',
                        'last_name': 'Boboka'
                    }
                ]
            },
            {
                'id': book_2.id,
                'name': 'Test book 2',
                'price': '55.00',
                'author_name': 'Author 1',
                'owner_name': None,
                'price_with_discount': None,
                'count_likes': 2,
                'rating': '3.5',
                'readers': [
                    {
                        'first_name': 'Ivan',
                        'last_name': 'Ivanov'
                    },
                    {
                        'first_name': 'Ivan',
                        'last_name': 'Sidorov'
                    },
                    {
                        'first_name': 'Ivan',
                        'last_name': 'Boboka'
                    }
                ]
            }
        ]
        self.assertEqual(expected_data, data)
