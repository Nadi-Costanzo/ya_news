from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.test.client import Client
from django.urls import reverse
from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Новость',
        text='Текст новости',
    )
    return news


@pytest.fixture
def eleven_news():
    today = datetime.today()
    News.objects.bulk_create(
        [
            News(
                title=f'Новость {index}',
                text=f'Текст новости № {index}',
                date=today - timedelta(days=index),
            )
            for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
        ]
    )
    # return News.objects.all()


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст новости',
    )
    return comment


@pytest.fixture
def three_comments(news, author):
    today = datetime.today()
    Comment.objects.bulk_create(
        [
            Comment(
                news=news,
                author=author,
                text=f'Текст комента {index}',
                created=today - timedelta(days=index),
            )
            for index in range(3)
        ]
    )


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def detail_url(news):
    return reverse('news:detail', args=(news.pk,))


@pytest.fixture
def url_to_comments(detail_url):
    url_to_comments = f"{detail_url}#comments"
    return url_to_comments


@pytest.fixture
def edit_comment_url(comment):
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def delete_comment_url(comment):
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def login_url():
    return reverse('users:login')


@pytest.fixture
def comments_form_data(news, author):
    return {
        'news': news.pk,
        'author': author.pk,
        'text': 'Некий другой текст',
    }
