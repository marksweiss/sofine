test:
	python ./sofine/tests/test_runner_from_cli.py
	python ./sofine/tests/test_runner_from_py.py
	python ./sofine/tests/test_runner_from_rest.py

test_examples:
	python ./sofine/tests/test_runner_from_py_examples.py
	
