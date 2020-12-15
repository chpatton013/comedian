.PHONY: clean dev_requirements dist dist_requirements dist_test example integration_test lint_test style_test test type_test unit_test

dev_requirements: dev_requirements.txt
	pip3 install --requirement dev_requirements.txt

dist_requirements: dist_requirements.txt
	pip3 install --requirement dist_requirements.txt

dist: dist_requirements
	python3 -OO -m PyInstaller \
	  --onefile \
	  --add-data=data/default.config.json:data/ \
	  --add-data=README.md:. \
	  --name=comedian \
	  ./src/__main__.py

clean:
	rm --recursive --force ./build
	rm --recursive --force ./dist
	rm --force ./comedian.spec

example:
	./src/__main__.py apply ./example.spec.json --mode=shell --quiet

test: style_test type_test lint_test unit_test integration_test dist_test

style_test: dev_requirements
	black --check .

type_test: dev_requirements
	find . -name '*.py' | xargs mypy

lint_test: dev_requirements
	find src tests -name '*.py' | xargs pylint

unit_test:
	cd tests/unit && python3 -m unittest

integration_test:
	cd tests/integration && python3 -m unittest

dist_test: dist
	bash -c 'diff ./README.md <(./dist/comedian --doc)'
