.PHONY: run
run:
	python -m uwb 2>&1 | tee -a uwb.log

.PHONY: run-without-log
run-without-log:
	python -m uwb

.PHONY: test
test:
	python -m unittest discover ./uwb/test
