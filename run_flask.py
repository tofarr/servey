"""
Python script for starting flask server for debugging / development
"""
if __name__ == '__main__':
    import os
    from servey.flask import configure_flask
    app = configure_flask()
    app.run(
        host=os.environ.get('FLASK_HOST') or '',
        port=int(os.environ.get('FLASK_PORT') or '8000'),
        debug=True
    )
