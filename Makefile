
install:
	pip install -U -r requirements.txt
	cp bin/gitl.py /usr/local/bin/gitl

dev:
	pip install -U -r requirements-dev.txt
