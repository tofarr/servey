This is very much a work in progress - I'll update this readme when it is production ready.

Philosophy: Get the most from AWS but allow local testing / not be completely dependent on it.

Actions Mounts, Handlers and Apps

Authorization should be explicit! That is why we inject it - one of the bits of magic

Why not use aws directly? Vendor lock in and lack of local test ability
Less flexibility than fastapi - common elements.

Why not include explicit caching? 
The more I think about this the more I think it is needed.

Authentication vs Authorization

Default implementation mostly meant to be as annoying as possible while still working


TODO:
* Finish aws integration
* Test Coverage
* Caching
* Example / Mock interfaces - provide example inputs in action for documentation / mocking / unit test generation

rate limiting needs persistence, but can be in access_control - maybe add to persisty goodies

python -m servey --sls-generate


```
pip install setuptools wheel
python setup.py sdist bdist_wheel
pip install twine
python -m twine upload dist/*
```