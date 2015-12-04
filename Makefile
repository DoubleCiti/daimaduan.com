check:
	@tox -e pep8

server:
	cd daimaduan && python runserver.py

install:
	sudo pip install -r requirements.txt