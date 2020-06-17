.PHONY: clean dist dist_test example test unit_test

dist:
	pip3 install --requirement dist_requirements.txt
	python3 -OO -m PyInstaller \
	  --onefile \
	  --add-data=default.config.json:. \
	  --add-data=README.md:. \
	  --name=comedian \
	  ./__main__.py

clean:
	rm --recursive --force ./build
	rm --recursive --force ./dist
	rm --force ./comedian.spec

example:
	./__main__.py apply ./example.spec.json --mode=shell --quiet

test: unit_test dist_test

unit_test:
	cd tests/unit && python3 -m unittest

dist_test: dist
	bash -c 'diff ./README.md <(./dist/comedian --doc)'
