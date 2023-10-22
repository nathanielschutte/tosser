clean:
	rm -f *.log

count:
	@find ./src -type f -name '*.py' -exec wc -l {} +
