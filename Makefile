install:
	docker run --rm -u 1000 -w /usr/src/app -v .:/usr/src/app python:3.14 python3 -m venv .venv
	docker run --rm -u 1000 -w /usr/src/app -v .:/usr/src/app python:3.14 bash -c "source .venv/bin/activate && pip3 install -U scikit-learn matplotlib"

extract:
	docker run --rm -w /usr/src/app -v .:/usr/src/app python:3.14 bash -c "source .venv/bin/activate && python lib/extract.py --generation-zero-samples 5 --generation-final-samples 10 --generation-zero 0 --generation-final 100 --seed 42"

run:
	docker run --rm -w /usr/src/app -v .:/usr/src/app python:3.14 bash -c "source .venv/bin/activate && python main.py 0.25 0.25 0.5"

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