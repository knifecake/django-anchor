.PHONY: test
test:
	uv run python tests/run.py

.PHONY: docs
docs:
	pushd docs && make html && popd
