import pytest
from django.conf import settings
from news.forms import CommentForm


@pytest.mark.django_db
def test_news_count(client, eleven_news, home_url):
    """
    Количество новостей на главной странице — не более 10.
    Новости отсортированы, cвежие новости в начале списка.
    """
    response = client.get(home_url)
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE

    # all_dates = [news.date for news in object_list]
    # sorted_dates = sorted(all_dates, reverse=True)
    sorted_news = sorted(object_list, key=lambda n: n.date, reverse=True)
    # assert all_dates == sorted_dates
    assert sorted_news == list(object_list)


@pytest.mark.django_db
def test_comments_count(client, three_comments, detail_url):
    """
    Комментарии на странице отдельной новости отсортированы в
    хронологическом порядке: старые в начале списка, новые — в конце.
    """
    response = client.get(detail_url)
    object_list = response.context['news'].comment_set.all()
    comments_count = object_list.count()
    assert comments_count == 3
    sorted_comments = sorted(
        object_list, key=lambda n: n.created, reverse=False
    )
    assert sorted_comments == list(object_list)


@pytest.mark.parametrize(
    'parametrized_client, form_in_context',
    (
        (pytest.lazy_fixture('author_client'), True),
        (pytest.lazy_fixture('client'), False),
    )
)
@pytest.mark.django_db
def test_detail_page_contains_form(
    detail_url, parametrized_client, form_in_context
):
    """
    Анонимному пользователю недоступна форма для отправки
    комментария на странице отдельной новости, а авторизованному доступна.
    """
    response = parametrized_client.get(detail_url)
    assert ('form' in response.context) is form_in_context
    if form_in_context:
        assert isinstance(response.context['form'], CommentForm)
