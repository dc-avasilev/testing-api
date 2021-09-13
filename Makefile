.ONESHELL:
.PHONY: tests

# Prepare tests
prepare_tests_local:
	. ./.venv/bin/activate
	pip3 install --upgrade pip
	pip3 install -r requirements.txt
	cp ./pytest.ini.dist ./pytest.ini

# Run testing
run_tests:
	pytest -vvv --test_env=${QA_ENV} ${QA_RUN_TEST}

run_all_tests_local:
	pytest -vvv tests

# Testing
tests:
	@make prepare_tests
	@make run_tests

tests_local:
	@make prepare_tests_local
	@make run_all_tests_local
