format:
	- isort --profile black .  
	- black -t py310 . 
	- autoflake -ri --remove-all-unused-imports .

errors:
	- pylint -E --output-format colorized v2/src

commit: format
	- git stage .
	- pythion make-commit -p no-version
	- git push