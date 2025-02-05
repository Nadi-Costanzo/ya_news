from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize(
    'name, news_object',
    (
        ('news:home', None),
        ('news:detail', pytest.lazy_fixture('news')),
    ),
)
@pytest.mark.django_db
def test_availability_for_anonymous_user(client, name, news_object):
    """-1- Проверка страниц, доступных анонимному пользователю."""
    if news_object is not None:
        url = reverse(name, args=(news_object.pk,))
    else:
        url = reverse(name)

    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
@pytest.mark.django_db
def test_pages_availability_for_different_users(
    parametrized_client, name, comment, expected_status
):
    url = reverse(name, args=(comment.pk,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
@pytest.mark.django_db
def test_redirect_for_anonymous_client(client, name, comment):
    """
    Проверка на редирект для неавторизированных пользователей при
    попытке перейти на страницу редактирования или удаления комментария.
    """
    login_url = reverse('users:login')
    url = reverse(name, args=(comment.pk,))
    redirect_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, redirect_url)


@pytest.mark.parametrize(
    'name',
    ('users:login', 'users:logout', 'users:signup'),
)
@pytest.mark.django_db
def test_availability_auth_urls_for_anonymous_user(client, name):
    """Проверка auth_urls, доступных анонимному пользователю."""
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
