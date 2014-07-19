test:
	python ./tests/test_runner_from_cli.py
	python ./tests/test_runner_from_py.py
	python ./tests/test_runner_from_rest.py

test_examples:
	python ./tests/test_runner_from_py_examples.py
	
