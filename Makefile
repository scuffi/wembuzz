compile-requirements:
	@echo "Compiling requirements..."
	@pip freeze > requirements.in
	@pip-compile --output-file=requirements.txt requirements.in

freeze: compile-requirements