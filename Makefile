install:
	docker run --rm -u 1000 -w /usr/src/app -v .:/usr/src/app python:3.14 python3 -m venv .venv
	docker run --rm -u 1000 -w /usr/src/app -v .:/usr/src/app python:3.14 bash -c "source .venv/bin/activate && pip3 install -U scikit-learn matplotlib"
	
select:
	docker run --rm -w /usr/src/app -v .:/usr/src/app python:3.14 bash -c "source .venv/bin/activate && python lib/select_individuals.py"

grouping_images:
	docker run --rm -w /usr/src/app -v .:/usr/src/app python:3.14 bash -c "source .venv/bin/activate && python grouping_images.py"

sorting_images:
	docker run --rm -w /usr/src/app -v .:/usr/src/app python:3.14 bash -c "source .venv/bin/activate && python sorting_images.py"

object_images:
	docker run --rm -w /usr/src/app -v .:/usr/src/app python:3.14 bash -c "source .venv/bin/activate && python object_images.py"

images:
	docker run --rm -w /usr/src/app -v .:/usr/src/app python:3.14 bash -c "source .venv/bin/activate && python grouping_images.py"\
	&& 	docker run --rm -w /usr/src/app -v .:/usr/src/app python:3.14 bash -c "source .venv/bin/activate && python sorting_images.py"\
	&& 	docker run --rm -w /usr/src/app -v .:/usr/src/app python:3.14 bash -c "source .venv/bin/activate && python object_images.py"

parsing:
	docker run --rm -w /usr/src/app -v .:/usr/src/app python:3.14 bash -c "source .venv/bin/activate && python parsing.py"

extract:
	docker run --rm -w /usr/src/app -v .:/usr/src/app python:3.14 bash -c "source .venv/bin/activate && python extract_features.py"