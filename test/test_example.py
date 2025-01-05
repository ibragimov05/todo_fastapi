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
