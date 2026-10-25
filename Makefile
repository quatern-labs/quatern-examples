.PHONY: test test-fast
test test-fast:
	python3 -m unittest discover -s tests
