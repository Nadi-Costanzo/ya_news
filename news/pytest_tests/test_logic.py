from http import HTTPStatus

import pytest
from news.forms import BAD_WORDS, WARNING
from news.models import Comment, News
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
def test_anonymous_user_cant_add_comment(
    client, detail_url, login_url, comments_form_data
):
    """Анонимный пользователь не может отправить комментарий."""
    response = client.post(detail_url, data=comments_form_data)
    expected_url = f'{login_url}?next={detail_url}'
    assertRedirects(response, expected_url)

    news = News.objects.get(pk=comments_form_data['news'])
    comments_count = news.comment_set.count()
    assert comments_count == 0


def test_user_can_add_comment(
        author_client, author, comments_form_data, detail_url,
):
    """Авторизованный пользователь может отправить комментарий."""
    response = author_client.post(detail_url, data=comments_form_data)
    expected_url = f"{detail_url}#comments"
    assertRedirects(response, expected_url)

    news = News.objects.get(pk=comments_form_data['news'])
    comments_count = news.comment_set.count()
    assert comments_count == 1

    # Проверяем значения полей комментария:
    new_comment = Comment.objects.get()
    assert new_comment.news_id == comments_form_data['news']
    assert new_comment.text == comments_form_data['text']
    assert new_comment.author == author


def test_user_cant_use_bad_words(author_client, detail_url, ):
    """Если комментарий содержит запрещённые слова, форма вернёт ошибку."""
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(detail_url, data=bad_words_data)
    assert response.status_code == HTTPStatus.OK
    assert response.context['form'].errors['text'][0] == WARNING


def test_author_can_edit_comment(
    author_client, author,
    comment, comments_form_data,
    url_to_comments, edit_comment_url
):
    """Автор может редактировать свои комментарии."""
    # Выполняем запрос на редактирование от имени автора комментария.
    response = author_client.post(edit_comment_url, data=comments_form_data)
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()

    new_comment = Comment.objects.get()
    assert new_comment.news_id == comments_form_data['news']
    assert new_comment.text == comments_form_data['text']
    assert new_comment.author == author


def test_other_user_cant_edit_comment(
    not_author_client, news, comment, comments_form_data,
    detail_url, url_to_comments, edit_comment_url, delete_comment_url
):
    """Др.пользователь НЕ может редактировать чужие комментарии."""
    # Выполняем запрос на редактирование от имени другого пользователя .
    response = not_author_client.post(
        edit_comment_url, data=comments_form_data
    )
    assert response.status_code == HTTPStatus.NOT_FOUND

    new_comment = Comment.objects.get(id=comment.id)
    assert new_comment.news_id == comment.news_id
    assert new_comment.text == comment.text
    assert new_comment.author == comment.author


def test_author_can_delete_note(
        author_client, news, delete_comment_url, url_to_comments
):
    """Автор может удалять свои комментарии."""
    response = author_client.post(delete_comment_url)
    assertRedirects(response, url_to_comments)
    comments_count = news.comment_set.count()
    assert comments_count == 0


def test_other_user_cant_delete_note(
        not_author_client, news, delete_comment_url
):
    """Др. пользователь не может удалять чужие комментарии."""
    response = not_author_client.post(delete_comment_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = news.comment_set.count()
    assert comments_count == 1
