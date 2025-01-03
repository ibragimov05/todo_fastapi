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
