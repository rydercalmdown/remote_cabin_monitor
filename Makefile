EMAIL_FROM="examplefrom@example.com"
EMAIL_TO="exampleto@example.com"

.PHONY: install
install:
	@. env/bin/activate && pip install -r src/requirements.txt

.PHONY: run
run:
	@. env/bin/activate \
		&& export EMAIL_FROM=$(EMAIL_FROM) \
		&& export EMAIL_TO=$(EMAIL_TO) \
		&& python src/app.py
