check:
	black --check .
	vulture
	pyright
run_frontend:
	cd text_highlighter/frontend && npm run start
run_backend:
	RELEASE=false streamlit run text_highlighter/__init__.py
build_frontend:
	cd text_highlighter/frontend && npm run build
build_backend:
	python setup.py sdist bdist_wheel
deploy_test: build_frontend build_backend
	python3 -m twine upload --repository testpypi dist/* --skip-existing
	python -m pip install --upgrade --index-url https://test.pypi.org/simple/ --no-deps text-highlighter
deploy_prod: build_frontend build_backend
	python3 -m twine upload dist/* --skip-existing
	python -m pip install --upgrade --no-deps text-highlighter
deploy: build_frontend build_backend
	python3 -m twine upload --repository testpypi dist/* --skip-existing
	python -m pip install --upgrade --index-url https://test.pypi.org/simple/ --no-deps text-highlighter
	python3 -m twine upload dist/* --skip-existing
	python -m pip install --upgrade --no-deps text-highlighter