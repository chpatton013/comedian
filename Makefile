.PHONY: clean dist example test

clean:
	rm --recursive --force ./build
	rm --recursive --force ./dist
	rm --force ./comedian.spec

dist:
	pip3 install --requirement requirements.txt
	python3 -OO -m PyInstaller \
      --onefile \
      --add-data=default.config.json:. \
      --add-data=README.md:. \
      --name=comedian \
      ./__main__.py

example:
	./__main__.py apply ./example.spec.json --mode=shell --quiet

test:
	cd tests && python3 -m unittest
