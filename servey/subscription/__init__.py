"""

Implementations:
    Starlette-Websocket:
        Client generates a subscriber_id and sends it along with the initial connection. Subsequent responses hit this.
    GraphQL-Strawberry:
        We add subscriptions to the schema. These listen on an iterator, and async yield items that match the channel
        id. Catch and close on disconnect. Iterator will have different implementaitons in clustered vs non clustered
        environments.
    Appsync:
        Build a mock mutation which can be invoked. Invoke will call the appsync mutation from the server side.
    ApiGateway:

"""
