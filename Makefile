
install:
	pip3 install --break-system-packages -U -r requirements.txt
	sudo cp src/gitl.py /usr/local/bin/gitl

install_dev:
	pip3 install -U -r requirements-dev.txt
