import pytest
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.test import Client
from questions.models import Question, QuestionAnswer, UserAnswer
from questions.utils import get_users_stats
from quizzes.models import Quiz


@pytest.mark.django_db
def test_start_quiz_view_correct(
    authenticated_client: Client, multiple_questions: None
) -> None:
    res_get = authenticated_client.get("/quizzes/")
    assert res_get.status_code == 200
    res_post = authenticated_client.post("/quizzes/", {"num_of_questions": 10})
    quizzes = Quiz.objects.all()
    assert quizzes.count() == 1
    questions = quizzes.first().questions.all()
    assert questions.count() == 10
    assert res_post.status_code == 302
    assert (
        res_post.url
        == f"/quizzes/{quizzes.first().pk}/question/{questions.first().pk}/"
    )


@pytest.mark.parametrize("method", ["put", "patch", "delete"])
def test_start_quiz_view_method_not_allowed(
    authenticated_client: Client, method: str
) -> None:
    res = getattr(authenticated_client, method)("/quizzes/")
    assert res.status_code == 405


@pytest.mark.django_db
def test_start_quiz_view_too_many_questions(
    authenticated_client: Client, multiple_questions: None
) -> None:
    questions_count = Question.objects.all().count()
    res = authenticated_client.post(
        "/quizzes/", {"num_of_questions": questions_count + 10}
    )
    assert res.status_code == 200
    assert (
        f"Not enough questions in db. Max number of questions: {questions_count}"
        in res.content.decode("utf-8")
    )


@pytest.mark.django_db
@pytest.mark.parametrize("out_of_range", ["question_id", "quiz_id"])
def test_quiz_question_view_quiz_not_exists(
    authenticated_client: Client, small_quiz: Quiz, out_of_range: str
) -> None:
    questions = sorted([question.pk for question in small_quiz.questions.all()])
    question_id = questions[-1]
    quiz_id = small_quiz.pk
    if out_of_range == "quiz_id":
        quiz_id += 1
    else:
        question_id += 1
    res = authenticated_client.get(f"/quizzes/{quiz_id}/question/{question_id}/")
    assert res.status_code == 404


@pytest.mark.django_db
@pytest.mark.parametrize(
    "route",
    [
        "/quizzes/",
        "/quizzes/{quiz_pk}/stats/",
        "/quizzes/{quiz_pk}/question/{question_pk}/",
        "/quizzes/{quiz_pk}/question/{question_pk}/answer/",
    ],
)
def test_quiz_routes_unauthorized(client: Client, small_quiz: Quiz, route: str) -> None:
    if "pk" in route:
        first_question = small_quiz.questions.first().pk
        route = route.format(quiz_pk=small_quiz.pk, question_pk=first_question)
    res = client.get(route)
    assert res.status_code == 302
    assert "/auth/login/" in res.url


@pytest.mark.django_db
def test_quiz_question_view_quiz_question_not_from_quiz(
    authenticated_client: Client, small_quiz
) -> None:
    all_questions = Question.objects.all()
    quiz_questions_pks = [question.pk for question in small_quiz.questions.all()]
    non_quiz_questions = [
        question.pk for question in all_questions.exclude(pk__in=quiz_questions_pks)
    ]
    res = authenticated_client.get(
        f"/quizzes/{small_quiz.pk}/question/{non_quiz_questions[0]}/"
    )
    assert res.status_code == 404


@pytest.mark.django_db
def test_quiz_question_view_correct(authenticated_client: Client, small_quiz) -> None:
    quiz_questions = [question.pk for question in small_quiz.questions.all()]
    first_question = quiz_questions[0]
    res = authenticated_client.get(
        f"/quizzes/{small_quiz.pk}/question/{first_question}/"
    )
    assert res.context["quiz_id"] == small_quiz.pk
    assert res.status_code == 200


@pytest.mark.parametrize("method", ["get", "put", "patch", "delete"])
def test_quiz_answer_view_method_not_allowed(
    authenticated_client: Client, method: str
) -> None:
    res = getattr(authenticated_client, method)("/quizzes/1/question/1/answer/")
    assert res.status_code == 405


@pytest.mark.django_db
@pytest.mark.parametrize(
    "content_type", ["multipart/form-data; boundary=BoUnDaRyStRiNg", "application/json"]
)
def test_quiz_answer_view_first_question(
    authenticated_client: Client, small_quiz: Quiz, content_type: str
) -> None:
    content_type_header: dict = (
        {"content_type": content_type} if "json" in content_type else {}
    )
    quiz_questions = [question.pk for question in small_quiz.questions.all()]
    first_question = quiz_questions[0]
    question_answer = QuestionAnswer.objects.filter(question=first_question).first()
    res = authenticated_client.post(
        f"/quizzes/{small_quiz.pk}/question/{first_question}/answer/",
        {"answer": question_answer.answer.pk},
        **content_type_header,
    )
    assert res.status_code == 200
    if content_type_header:
        content = res.json()
        assert content["correct"] == question_answer.correct
        assert content["quiz_id"] == small_quiz.pk
        assert content["next_question"] != first_question
    else:
        expected_msg = (
            "Success! Correct answer" if question_answer.correct else "Incorrect answer"
        )
        assert expected_msg in res.content.decode("utf-8")
        assert res.context["quiz_id"] == small_quiz.pk
        assert res.context["next_question"] != first_question


@pytest.mark.django_db
def test_quiz_answer_view_second_question(
    authenticated_client: Client, small_quiz: Quiz
) -> None:
    quiz_questions = [question.pk for question in small_quiz.questions.all()]
    first_question = quiz_questions[0]
    another_question = quiz_questions[1]
    question_answered = QuestionAnswer.objects.filter(question=first_question).first()
    user = User.objects.get(pk=authenticated_client.session["_auth_user_id"])
    UserAnswer.objects.create(
        author=user, quiz=small_quiz, question_answer=question_answered
    )
    new_qa = QuestionAnswer.objects.filter(question=another_question).first()
    res = authenticated_client.post(
        f"/quizzes/{small_quiz.pk}/question/{another_question}/answer/",
        {"answer": new_qa.answer.pk},
    )
    expected_msg = "Success! Correct answer" if new_qa.correct else "Incorrect answer"
    assert expected_msg in res.content.decode("utf-8")
    assert res.context["quiz_id"] == small_quiz.pk
    assert res.context["next_question"] in quiz_questions
    assert res.context["next_question"] != first_question
    assert res.context["next_question"] != another_question
    assert res.status_code == 200


@pytest.mark.django_db
@pytest.mark.parametrize(
    "content_type", ["multipart/form-data; boundary=BoUnDaRyStRiNg", "application/json"]
)
def test_quiz_answer_view_last_question(
    authenticated_client: Client, small_quiz: Quiz, content_type: str
) -> None:
    content_type_header: dict = (
        {"content_type": content_type} if "json" in content_type else {}
    )
    quiz_questions = [question.pk for question in small_quiz.questions.all()]
    last_question = quiz_questions[-1]
    user = User.objects.get(pk=authenticated_client.session["_auth_user_id"])
    for question in quiz_questions[:-1]:
        question_answer = QuestionAnswer.objects.filter(question=question).first()
        UserAnswer.objects.create(
            author=user, quiz=small_quiz, question_answer=question_answer
        )
    question_answer = QuestionAnswer.objects.filter(question=last_question).first()
    res = authenticated_client.post(
        f"/quizzes/{small_quiz.pk}/question/{last_question}/answer/",
        {"answer": question_answer.answer.pk},
        **content_type_header,
    )
    message = get_messages(res.wsgi_request)._queued_messages[0].message
    assert res.status_code == 302
    assert res.url == f"/quizzes/{small_quiz.pk}/stats/"
    assert "It was the last question. Check your stats and start a new quiz." in message


@pytest.mark.django_db
def test_quiz_stats_view(
    authenticated_client: Client, finished_quiz: Quiz, user_answers: None
) -> None:
    res = authenticated_client.get(f"/quizzes/{finished_quiz.pk}/stats/")
    assert res.status_code == 200
    quiz_answers = UserAnswer.objects.filter(quiz=finished_quiz)
    stats = get_users_stats(quiz_answers)
    if stats.correct_percent < 80:
        assert (
            f"You have had {stats.correct_percent}% answers correctly"
            in res.content.decode("utf-8")
        )
    else:
        assert "Awesome! You nailed it!" in res.content.decode("utf-8")


@pytest.mark.parametrize("method", ["post", "put", "patch", "delete"])
def test_quiz_stats_view_method_not_allowed(
    authenticated_client: Client, method: str
) -> None:
    res = getattr(authenticated_client, method)("/quizzes/1/stats/")
    assert res.status_code == 405


@pytest.mark.django_db
def test_quiz_stats_out_of_range_view(
    authenticated_client: Client, finished_quiz: Quiz, user_answers: None
) -> None:
    res = authenticated_client.get(f"/quizzes/{finished_quiz.pk + 100}/stats/")
    message = get_messages(res.wsgi_request)._queued_messages[0].message
    assert res.status_code == 302
    assert "Quiz doesn't exist" in message
    assert "/quizzes/" == res.url
