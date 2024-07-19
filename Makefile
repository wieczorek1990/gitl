
install:
	pip3 install -U -r requirements.txt
	sudo cp bin/gitl.py /usr/local/bin/gitl

install_dev:
	pip3 install -U -r requirements-dev.txt
