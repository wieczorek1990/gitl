install:
	sudo uv pip install --system -U gnureadline
	mkdir -p ~/.local/bin/
	cp src/gitl.py ~/.local/bin/gitl

dependencies:
	uv pip install -U -r requirements-dev.txt
