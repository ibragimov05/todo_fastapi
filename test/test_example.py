import pytest


def test_equal_or_not_equal():
	assert 1 == 1
	assert 1 != 2


def test_is_instance():
	assert isinstance(1, int)
	assert not isinstance(1, str)


def test_boolean():
	validated = True

	assert validated is True
	assert ("Hello" == "world") is False


def test_type():
	assert type('Hello' is str)
	assert type('world' is not int)


def test_greater_and_less_than():
	assert 1 > 0
	assert 1 < 2


def test_list():
	nums_list = [1, 2, 3]
	any_list = [False, False]

	assert 1 in nums_list
	assert 7 not in nums_list
	assert all(nums_list)
	assert not any(any_list)


class Student:
	def __init__(self, first_name: str, last_name: str, major: str, years: int):
		self.first_name = first_name
		self.last_name = last_name
		self.major = major
		self.years = years


@pytest.fixture
def default_employee() -> Student:
	return Student('John', 'Doe', 'Computer Science', 4)


def test_person_initialization(default_employee):
	assert default_employee.first_name == 'John', 'First name should be John'
	assert default_employee.last_name == 'Doe', 'Last name should be Doe'
	assert default_employee.major == 'Computer Science'
	assert default_employee.years == 4
