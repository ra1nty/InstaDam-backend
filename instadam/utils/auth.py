from functools import wraps
from flask import request, g, jsonify, current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired, BadSignature

TWO_WEEKS = 1209600

def generate_token(user, expiration=TWO_WEEKS):
    """Generates JSON Web token for a given user object

    Args:
        user: The given user object
        expiration: The lifespan of the token, default is 2 weeks
    """
    s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
    token = s.dumps({
        'id': user.id,
        'username': user.username,
    }).decode('utf-8')
    return token


def verify_token(token):
    """Parse JSON Web token

    Args:
        token: The given token
    
    Returns:
        A dict which is parsed token payload
        {'id': user
        'username' : username}
    """
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
    except SignatureExpired:
        return None # valid token, but expired
    except BadSignature:
        return None # invalid token
    return data


def requires_auth(f):
    """A function decorator to require authorization.
    
    We first verify the token and parsed the logined user
    into the flask global env. If the token is invalid or
    deformed a 401 Unauthorized error will be returned directly.

    Args:
        f: function
    
    Returns:
        A decoreator
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', None)
        if token:
            token = token.encode('ascii', 'ignore')
            user = verify_token(token)
            if user:
                g.user = user
                return f(*args, **kwargs)
        return jsonify({
            'message' : 'Authentication required.'
        }), 401
    return decorated
