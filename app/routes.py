from flask import Blueprint, request, jsonify
from .identify import identify_user

identify_bp = Blueprint('identify', __name__)

@identify_bp.route('/identify', methods=['POST'])
def identify():
    data = request.get_json()
    return identify_user(data)
