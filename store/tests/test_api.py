import json

from django.contrib.auth.models import User
from django.db.models import Count, Case, When, F
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APITestCase

from store.models import Book, UserBookRelation
from store.serializers import BooksSerializer, UserBookRelationSerializer


class BooksApiTestCase(APITestCase):
    """
    Тестирование Books API
    """
    def setUp(self):
        """
        Предварительная настройка параметров
        """
        self.user = User.objects.create(username='test_user')
        self.book_1 = Book.objects.create(name='Test book', price=25,
                                          author_name='Author 4', owner=self.user)
        self.book_2 = Book.objects.create(name='Test book 2', price=55,
                                          author_name='Author 1')
        self.book_3 = Book.objects.create(name='Test book Author 1', price=55,
                                          author_name='Author 2')
        self.book_4 = Book.objects.create(name='Test book 4', price=35,
                                          author_name='Author 3')
        UserBookRelation.objects.create(user=self.user, book=self.book_1, like=True, rate=5)

    def test_get(self):
        """
        Тестирование get запроса неавторизованным пользователем
        """
        url = reverse('book-list')
        response = self.client.get(url, format='json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        books = Book.objects.all().annotate(
            count_likes=Count(Case(When(userbookrelation__like=True, then=1))),
            price_with_discount=F('price') - F('discount'),
            owner_name=F('owner__username')
        ).prefetch_related('readers').order_by('id')
        serializer_data = BooksSerializer(books, many=True).data
        self.assertEqual(serializer_data, response.data['results'])
        self.assertEqual(serializer_data[0]['count_likes'], 1)
        self.assertEqual(serializer_data[0]['rating'], '5.0')

    def test_get_filter(self):
        """
        Тестирование get c использованеим фильтра по price неавторизованным пользователем
        """
        url = reverse('book-list')
        response = self.client.get(url, data={'price': 55}, format='json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        books = Book.objects.filter(id__in=[self.book_2.id, self.book_3.id]).annotate(
            count_likes=Count(Case(When(userbookrelation__like=True, then=1))),
            price_with_discount=F('price') - F('discount'),
            owner_name=F('owner__username')
        ).prefetch_related('readers').order_by('id')
        serializer_data = BooksSerializer(books, many=True).data
        self.assertEqual(serializer_data, response.data['results'])

    def test_get_search(self):
        """
        Тестирование get c использованеим поиска по 'Author 1' по полям 'name', 'author_name'
        """
        url = reverse('book-list')
        response = self.client.get(url, data={'search': 'Author 1'}, format='json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        books = Book.objects.filter(id__in=[self.book_2.id, self.book_3.id]).annotate(
            count_likes=Count(Case(When(userbookrelation__like=True, then=1))),
            price_with_discount=F('price') - F('discount'),
            owner_name=F('owner__username')
        ).prefetch_related('readers').order_by('id')
        serializer_data = BooksSerializer(books, many=True).data
        self.assertEqual(serializer_data, response.data['results'])

    def test_get_ordering_price(self):
        """
        Тестирование get c использованеим сортировки по price
        """
        url = reverse('book-list')
        response = self.client.get(url, data={'ordering': 'price'}, format='json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        books = Book.objects.all().annotate(
            count_likes=Count(Case(When(userbookrelation__like=True, then=1))),
            price_with_discount=F('price') - F('discount'),
            owner_name=F('owner__username')
        ).prefetch_related('readers').order_by('price')
        serializer_data = BooksSerializer(books, many=True).data
        self.assertEqual(serializer_data, response.data['results'])

    def test_get_ordering_author(self):
        """
        Тестирование get c использованеим сортировки по author_name
        """
        url = reverse('book-list')
        response = self.client.get(url, data={'ordering': 'author_name'}, format='json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        books = Book.objects.all().annotate(
            count_likes=Count(Case(When(userbookrelation__like=True, then=1))),
            price_with_discount=F('price') - F('discount'),
            owner_name=F('owner__username')
        ).prefetch_related('readers').order_by('author_name')
        serializer_data = BooksSerializer(books, many=True).data
        self.assertEqual(serializer_data, response.data['results'])

    def test_create(self):
        """
        test_create проверка на создание книги в модели
        """
        first_count_book = Book.objects.all().count()
        url = reverse('book-list')
        data = {
            'name': 'Programming in Python 3',
            'price': 150,
            'author_name': 'Mark Summerfield'
        }
        json_data = json.dumps(data)

        # логиним пользователя
        self.client.force_login(self.user)

        # запрос на create
        response = self.client.post(url, data=json_data, content_type='application/json')

        # проверяем статус
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

        # проверяем, что количество книг увеличилось на 1
        self.assertEqual(first_count_book + 1, Book.objects.all().count())

        # тестирование присвоения книги user
        self.assertEqual(self.user, Book.objects.last().owner)

    def test_update(self):
        """
        test_update проверка на изменение
        """
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {
            'name': self.book_1.name,
            'price': 575,
            'author_name': self.book_1.name
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.put(url, data=json_data, content_type='application/json')
        self.book_1.refresh_from_db()
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(575, self.book_1.price)

    def test_update_not_owner(self):
        """
        test_update проверка на изменение не владельцем книги, а дургим авторизованным пользователем
        """
        user2 = User.objects.create(username='test_user2')
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {
            'name': self.book_1.name,
            'price': 575,
            'author_name': self.book_1.name
        }
        json_data = json.dumps(data)
        self.client.force_login(user2)
        response = self.client.put(url, data=json_data,
                                   content_type='application/json')

        self.book_1.refresh_from_db()
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEqual({'detail': ErrorDetail(string='You do not have permission to perform this action.',
                                                code='permission_denied')}, response.data)
        self.assertEqual(25, self.book_1.price)

    def test_update_not_owner_but_staff(self):
        """
        test_update проверка на изменение не владельцем книги, а пользователем с правами staff
        """
        user2 = User.objects.create(username='test_user2',
                                    is_staff=True)
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {
            'name': self.book_1.name,
            'price': 575,
            'author_name': self.book_1.name
        }
        json_data = json.dumps(data)
        self.client.force_login(user2)
        response = self.client.put(url, data=json_data, content_type='application/json')
        self.book_1.refresh_from_db()
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(575, self.book_1.price)

    def test_delete(self):
        """
        Тестирование удаления пользователем книги, который является её владельцем
        """
        first_count_books = Book.objects.all().count()
        url = reverse('book-detail', args=(self.book_1.id,))
        self.client.force_login(self.user)
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(first_count_books - 1, Book.objects.all().count())

    def test_delete_not_owner(self):
        """
        Тестирование удаления пользователем книги, который не является её владельцем
        """
        user2 = User.objects.create(username='test_user2')
        first_count_books = Book.objects.all().count()
        url = reverse('book-detail', args=(self.book_1.id,))
        self.client.force_login(user2)
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEqual({'detail': ErrorDetail(string='You do not have permission to perform this action.'
                                                , code='permission_denied')}, response.data)
        self.assertEqual(first_count_books, Book.objects.all().count())

    def test_delete_not_owner_but_staff(self):
        """
        Тестирование удаления книги пользователем с правами staff
        """
        user2 = User.objects.create(username='test_user2',
                                    is_staff=True)
        first_count_books = Book.objects.all().count()
        url = reverse('book-detail', args=(self.book_1.id,))
        self.client.force_login(user2)
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(first_count_books - 1, Book.objects.all().count())


class BooksRelationsApiTestCase(APITestCase):
    """
    Тестирование RelationsAPI
    """
    def setUp(self):
        self.user = User.objects.create(username='test_user')
        self.user2 = User.objects.create(username='test_user2')
        self.book_1 = Book.objects.create(name='Test book', price=25,
                                          author_name='Author 4', owner=self.user)
        self.book_2 = Book.objects.create(name='Test book 2', price=55,
                                          author_name='Author 1')
        self.book_3 = Book.objects.create(name='Test book Author 1', price=55,
                                          author_name='Author 2')
        self.book_4 = Book.objects.create(name='Test book 4', price=35,
                                          author_name='Author 3')

    def test_patch_ok(self):
        """
        Ставим лайк
        """
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))
        data = {
            'like': True,
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user,
                                                book=self.book_1)
        print(relation)

    def test_like_and_bookmarks(self):
        """
            Ставим лайк и добавляем в избранное
        """
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))
        data = {
            'like': True,
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user,
                                                book=self.book_1)
        self.assertTrue(relation.like)
        data = {
            'in_bookmarks': True,
        }
        json_data = json.dumps(data)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user,
                                                book=self.book_1)
        self.assertTrue(relation.in_bookmarks)

    def test_rate(self):
        """
            Ставим оценку
        """
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))
        data = {
            'rate': 3,
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user,
                                                book=self.book_1)
        self.assertEqual(3, relation.rate)

    def test_rate_wrong(self):
        """
            Ставим оценку, которая не пройдёт валицацию
        """
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))
        data = {

            'rate': 6,

        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code, response.data)
        relation = UserBookRelation.objects.get(user=self.user,
                                                book=self.book_1)
        self.assertEqual(None, relation.rate)

    def test_put_ok(self):
        """
        Оценка определённой книги
        """
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))
        data = {
            'book': self.book_1.id,
            'like': True,
            'in_bookmarks': True,
            'rate': 3,
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.put(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user,
                                                book=self.book_1)
        relation_data = UserBookRelationSerializer(relation).data
        self.assertEqual(relation_data, response.data)
