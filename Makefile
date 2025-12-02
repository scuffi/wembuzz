compile-requirements:
	@echo "Compiling requirements..."
	@pip freeze > requirements.in
	@pip-compile --output-file=requirements.txt requirements.in

freeze: compile-requirements

mongo-up:
	@echo "Starting MongoDB in Docker..."
	@docker run -d \
		--name wembuzz-mongodb \
		-p 27017:27017 \
		-v wembuzz-mongodb-data:/data/db \
		mongo:latest || \
	(docker start wembuzz-mongodb && echo "MongoDB container already exists, starting it...")
	@echo "MongoDB is running on localhost:27017"

mongo-down:
	@echo "Stopping MongoDB container..."
	@docker stop wembuzz-mongodb 2>/dev/null || true
	@docker rm wembuzz-mongodb 2>/dev/null || true
	@echo "MongoDB container stopped and removed"

departure-board:
	@echo "Running departure board example..."
	@python -m apps.departure_board.main
