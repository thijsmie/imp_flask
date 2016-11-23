PYCODE = import flask.ext.statics as a; print a.__path__[0]
.PHONY: default isvirtualenv

default:
	@echo "Local examples:"
	@echo "    make run        # Starts a Flask development server locally."
	@echo "    make shell      # Runs 'manage.py shell' locally with iPython."
	@echo "    make style      # Check code styling with flake8."
	@echo "    make lint       # Runs PyLint."
	@echo "    make test       # Tests entire application with pytest."

isvirtualenv:
	@if [ -z "$(VIRTUAL_ENV)" ]; then echo "ERROR: Not in a virtualenv." 1>&2; exit 1; fi

run:
	(((i=0; while \[ $$i -lt 40 \]; do sleep 0.5; i=$$((i+1)); \
		netstat -anp tcp |grep "\.5000.*LISTEN" &>/dev/null && break; done) && open http://localhost:5000/) &)
	./manage.py devserver

shell:
	./manage.py shell

style:
	flake8 --max-line-length=120 --statistics imp_flask

lint:
	pylint --max-line-length=120 imp_flask

test:
	py.test --cov-report term-missing --cov imp_flask tests

testpdb:
	py.test --pdb tests

testcovweb:
	py.test --cov-report html --cov imp_flask tests
	open htmlcov/index.html

pipinstall: isvirtualenv
	# For development environments. Symlinks are for PyCharm inspections to work with Flask-Statics-Helper.
	pip install -r requirements.txt flake8 pylint ipython pytest-cov
	[ -h pypi_portal/templates/flask_statics_helper ] || ln -s `python -c "$(PYCODE)"`/templates/flask_statics_helper \
		pypi_portal/templates/flask_statics_helper
	[ -h pypi_portal/static/flask_statics_helper ] || ln -s `python -c "$(PYCODE)"`/static \
		pypi_portal/static/flask_statics_helper

