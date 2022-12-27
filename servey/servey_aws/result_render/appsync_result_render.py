
* For each resolver on an endpoint from an action, we can create a resolver lambda (Similar to the invoker lambda)
    * The resolver lambda will have environment variables
        * The module being resolved
        * The type being resolved
        * The function, being resolved
    * We use the marshaller to try and create a type instance. Then we invoke the resolver and return it

* Batching is enabled on all invoker lambdas. They can have multiple events and responses. If they have a
  `batch resolver` defined, we use this. This needs to be backported back into strawberry.


* a resolvable can be an action?
e.g: resolvable(action_name="", attr_mapping="")



Caching? Appsync has built in caching which we make use of. we set up a ttl cache on each item. (Max ttl is 3600)