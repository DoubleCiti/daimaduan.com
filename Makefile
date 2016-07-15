check:
	@tox -e pep8

server:
	honcho start

install:
	sudo pip install -r requirements.txt