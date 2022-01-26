if __name__ == '__main__':
    import os
    from old2.websocket.single_node_websocket_connector import SingleNodeWebsocketConnector
    connector = SingleNodeWebsocketConnector(
        host=os.environ.get('WEBSOCKET_HOST') or 'localhost',
        port=os.environ.get('WEBSOCKET_PORT') or 8001
    )
    connector.start()
