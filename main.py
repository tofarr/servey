from old.client.http_service_client_abc import HttpServiceClientABC
from old.handler.action_handler import service_handler

'''
@http_callable(url="https://localhost:3000/say_hello")
def say_hello_remote(name: str) -> str:
    """ Say hello to the name given """
'''

class HelloServiceClient(HttpServiceClientABC):
    __root_url__ = 'http://localhost:3000/'

    @staticmethod
    def say_hello(name: str) -> str:
        """ No implementation """


class HelloService:

    @staticmethod
    def say_hello(name: str = 'Doofus') -> str:
        return f'Hello {name}!'


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    service = HelloService()
    handler = service_handler(service)

    client = HelloServiceClient()
    print(client.say_hello(name='Tim'))



# See PyCharm help at https://www.jetbrains.com/help/pycharm/
