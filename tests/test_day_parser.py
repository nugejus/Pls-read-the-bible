import pytest
from utilities import DayParser

test_case = {
    "1-3일차 완료": [1, 2, 3],
    "1~5일차 완료": [1, 2, 3, 4, 5],
    "1-7 일차 완료": [1, 2, 3, 4, 5, 6, 7],
}

parser = DayParser()


@pytest.mark.parametrize("test,expected", test_case.items())
def test_continues_date(test, expected):
    assert parser.parse(test) == expected


test_case = {
    "1,3,4일차 완료": [1, 3, 4],
    "2,5,6,7 일차 완료": [2, 5, 6, 7],
    "3일차 완료": [3],
}


@pytest.mark.parametrize("test,expected", test_case.items())
def test_discret_date(test, expected):
    assert parser.parse(test) == expected


test = {
    "1일차 통독 완료": [1],
    "1일차 성경읽기 완료": [1],
    "성경읽기 1일차 완료": [1],
    "1일차 완료했습니다": [1],
    "1일차 완료.\n창세가 1장\n[1]하나님께서 천지를 창조하시니라": [1],
}


@pytest.mark.parametrize("test,expected", test_case.items())
def test_with_plus_words(test, expected):
    assert parser.parse(test) == expected


test = {
    "1일차 통독 클리어": [1],
    "1일차 성경읽기 클리어": [1],
    "성경읽기 1일차 클리어": [1],
    "1일차 클리어했습니다": [1],
    "1,3,4일차 클리어": [1, 3, 4],
    "2,5,6,7 일차 클리어": [2, 5, 6, 7],
    "3일차 클리어": [3],
}


@pytest.mark.parametrize("test,expected", test_case.items())
def test_with_word_clear(test, expected):
    assert parser.parse(test) == expected


test = {
    "332, 334-339, 341일차 완료!": [332, 334, 335, 336, 337, 338, 339, 341],
    "1-3, 5일차 완료": [1, 2, 3, 5],
}


@pytest.mark.parametrize("test,expected", test_case.items())
def test_descrete_with_continues(test, expected):
    assert parser.parse(test) == expected
