install:
	mkdir -p ~/.local/bin/
	cp src/gitl.py ~/.local/bin/gitl

dependencies:
	pip3 install -U -r requirements-dev.txt
