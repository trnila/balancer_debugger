all: ui_control.py

ui_%.py: %.ui
	pyuic5 $^ -o $@

clean:
	rm -f ui_*.py

