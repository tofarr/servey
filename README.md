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
* Integrate with strawberry
* Finish serverless integration
* Remote actions
* Test Coverage

rate limiting needs persistence, but can be in access_control - maybe add to persisty goodies