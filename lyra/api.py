"""
Flask REST API for LYRA AI.
Provides endpoints for quantum simulations, wisdom search, and scientific models.
"""

from flask import Blueprint, Flask, jsonify, request
from werkzeug.exceptions import BadRequest

from .quantum import quantum_simulation
from .models import simulate_collapse
from .wisdom import WisdomDatabase

# Create a Blueprint for the API
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Initialize Wisdom Database
wisdom_db = WisdomDatabase()


@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'version': '0.1.0',
        'endpoints': [
            '/api/health',
            '/api/wisdom',
            '/api/quantum',
            '/api/collapse'
        ]
    }), 200


@api_bp.route('/wisdom', methods=['GET'])
def search_wisdom():
    """
    Search the Wisdom Database.

    Query Parameters:
    - query (str): Search term for wisdom quotes.
    - limit (int): Maximum number of results (default: 5).
    - tag (str): Filter by tag.
    - author (str): Filter by author.
    - random (bool): Return random quotes if True.

    Returns:
        JSON: List of matching quotes.
    """
    query = request.args.get('query', '')
    limit = int(request.args.get('limit', 5))
    tag = request.args.get('tag', None)
    author = request.args.get('author', None)
    random = request.args.get('random', 'false').lower() == 'true'

    if random:
        results = wisdom_db.get_random(limit=limit)
    elif tag:
        results = wisdom_db.get_by_tag(tag, limit=limit)
    elif author:
        results = wisdom_db.get_by_author(author, limit=limit)
    elif query:
        results = wisdom_db.search(query, limit=limit)
    else:
        msg = "At least one of query, tag, author, or random=true must be provided"
        raise BadRequest(msg)

    return jsonify({
        'count': len(results),
        'results': results
    }), 200


@api_bp.route('/quantum', methods=['GET'])
def quantum_simulation_api():
    """
    Run a quantum circuit simulation.

    Query Parameters:
    - theta (float): Rotation angle in radians (default: 0.0).

    Returns:
        JSON: Result of the quantum simulation (expectation value of PauliZ).
    """
    theta = float(request.args.get('theta', 0.0))
    result = quantum_simulation(theta)

    return jsonify({
        'theta': theta,
        'result': result,
        'interpretation': 'Expectation value of PauliZ operator (range: [-1, 1])'
    }), 200


@api_bp.route('/collapse', methods=['GET'])
def collapse_simulation_api():
    """
    Simulate informational collapse dynamics.

    Query Parameters:
    - alpha_G (float): Coupling constant for the collapse process (default: 1.0).
    - points (int): Number of time points to simulate (default: 100).

    Returns:
        JSON: Time series of informational gradient values.
    """
    alpha_G = float(request.args.get('alpha_G', 1.0))
    results = simulate_collapse(alpha_G=alpha_G)

    return jsonify({
        'alpha_G': alpha_G,
        'time_points': len(results),
        'values': results,
        'interpretation': 'Informational gradient over time (decaying exponential)'
    }), 200


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.register_blueprint(api_bp)
    return app


# Create a default app instance for direct import
app = create_app()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
