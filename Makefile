init:
	@[ -f model_endpoints.yml ] && echo "model_endpoints.yml already exists." || (cp model_endpoints_template.yml model_endpoints.yml && echo "model_endpoints.yml created. Please fill it with your API keys.")
	@[ -f .env ] && echo ".env already exists." || (cp .env.example .env && echo ".env created.")
	@echo "Project initialized."

build:
	docker build -t ebiose .

run:
	docker run -it --env-file .env -v $(CURDIR)/model_endpoints.yml:/app/model_endpoints.yml ebiose
