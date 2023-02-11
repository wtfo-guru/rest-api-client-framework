mypy:
	mypy --install-types --non-interactive gawsoft/

test:
	pytest tests/

release-test:
	python -m build --no-isolation
	twine check dist/*
	twine upload -r testpypi dist/* --config-file ./.pypirc --verbose

release:
	python -m build --no-isolation
	twine check dist/*
	twine upload dist/* --config-file ./.pypirc --verbose
