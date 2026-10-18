"""Week-1 entry point. Upstream implementation remains in Git history."""
import os
from clinic_app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000,
            debug=os.getenv('FLASK_DEBUG', '').lower() == 'true')
