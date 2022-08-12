Philosophy: Get the most from AWS but allow local testing / not be completely dependent on it.

Authorization should be explicit! That is why we inject it - one of the bits of magic

Why not use aws directly? Vendor lock in and lack of local test ability
Less flexibility than fastapi - common elements.

Why not include explicit caching? 
The more I think about this the more I think it is needed.

Why not include graphql?

TODO:
* Finish Auth
* NO Implement caching
* Implement route pluggability (Will be used in persisty)
* Think about integration with persisty caching
* Integrate with dramatiq for scheduling
* Finish serverless integration

ActionMeta
Action

Mounts

Remote Actions
http_action
lambda_action

rate limiting needs persistence, but can be in access_control