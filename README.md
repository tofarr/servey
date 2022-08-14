Philosophy: Get the most from AWS but allow local testing / not be completely dependent on it.

Actions Mounts, and Apps

Authorization should be explicit! That is why we inject it - one of the bits of magic

Why not use aws directly? Vendor lock in and lack of local test ability
Less flexibility than fastapi - common elements.

Why not include explicit caching? 
The more I think about this the more I think it is needed.

Authentication vs Authorization

Default implementation mostly meant to be as annoying as possible while still working

Why not include graphql?

TODO:
* NO Implement caching
* Injection / Outjection? Other items from the context 
  - Like what? DB Connection? No.
    Cache headers? (Like an ETag - Good call. From request but not.)
    Feels like not everything needs auth.
    Graphql directives? I feel like graphql does not work well with this model and needs its own - Like it should
    control the narrative rather than vice versa.
    
    
    
* General purpose injection vs authentication.
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