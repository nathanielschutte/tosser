clean:
	rm -f *.log

test: static-analysis lint unit-tests

static-analysis:
	mypy src --ignore-missing-imports

lint:
	flake8 src --max-line-length=120 --ignore=E203,W503,W293

unit-tests:
	pytest -k 'not transactions'

count:
	@find ./src -type f -name '*.py' -exec wc -l {} + | sort -n
