test:
	python ./sofine/tests/test_runner_from_cli.py
	python ./sofine/tests/test_runner_from_py.py
	python ./sofine/tests/test_runner_from_rest.py

test_examples:
	python ./sofine/tests/test_runner_from_py_examples.py

docs:
	./make_docs

docs_static:
	git checkout gh-pages
	git merge master
	git add -A
	git commit -m "Updated static documentation."
	git push origin gh-pages
	git checkout master
