clean:
	@find . -name "*.pyc" | xargs rm -rf
	@find . -name "*.pyo" | xargs rm -rf
	@find . -name "__pycache__" -type d | xargs rm -rf

test: clean
	py.test -x health_check

coverage: clean
	py.test -x --cov-config .coveragerc --cov-report html --cov-report term --cov health_check

requirements:
	pip install -r requirements.txt
