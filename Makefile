install:
	pip install -U gnureadline
	mkdir -p ~/.local/bin/
	cp src/gitl.py ~/.local/bin/gitl

dependencies:
	pip install -U -r requirements-dev.txt
