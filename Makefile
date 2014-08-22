deploy:
	@rm -rf dist > /dev/null
	@rm -rf sofine.egg-info > /dev/null
	@rm -rf $$PYTHONPATH/sofin* > /dev/null
	@python setup.py sdist --formats=gztar,zip > /dev/null
	@pip install --allow-unverified --no-index --find-links dist sofine > /dev/null

test: deploy
	python ./sofine/tests/test_runner_from_cli.py
	python ./sofine/tests/test_runner_from_py.py
	python ./sofine/tests/test_runner_from_rest.py
	python ./sofine/tests/test_format_csv.py

test_examples: deploy
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
