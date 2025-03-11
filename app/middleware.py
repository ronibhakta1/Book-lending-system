from functools import wraps
import jwt
from flask import request, jsonify
from app import create_app  # Absolute import
from app.models import User  # Absolute import

app = create_app()
def token_required(f):
    # The `@wraps(f)` decorator is used to preserve the metadata of the original function `f` when
    # creating a wrapper function. It copies the attributes such as `__name__`, `__doc__`, and
    # `__module__` from the original function `f` to the wrapper function `decorated`. This is helpful
    # for maintaining the identity of the original function for debugging, logging, and other
    # purposes. It ensures that the wrapper function behaves as closely as possible to the original
    # function it is decorating.
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or not token.startswith('Bearer '):
            return jsonify({'message': 'Token is missing or invalid'}), 401
        try:
            token = token.split(" ")[1]
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.get(data['user_id'])
            if not current_user:
                return jsonify({'message': 'User not found'}), 401
        except:
            return jsonify({'message': 'Token is invalid'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

def librarian_required(f):
    @wraps(f)
    @token_required
    def decorated(current_user, *args, **kwargs):
        if current_user.role != 'librarian':
            return jsonify({'message': 'Librarian access required'}), 403
        return f(current_user, *args, **kwargs)
    return decorated