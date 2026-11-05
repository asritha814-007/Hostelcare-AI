import json
import os
from flask import Blueprint, jsonify
from database import get_stats
from config import Config

stats_bp = Blueprint('stats', __name__)

FAQS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'nlp', 'dataset', 'faqs.json')

@stats_bp.route('/api/stats', methods=['GET'])
def stats():
    counts = get_stats()
    return jsonify({
        "success": True,
        "data": counts
    })

@stats_bp.route('/api/guide', methods=['GET'])
def get_guide():
    with open(FAQS_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    faqs = data.get('faqs', [])
    categories = {}
    for item in faqs:
        cat = item.get('category', 'General')
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(item)

    return jsonify({
        "success": True,
        "total_articles": len(faqs),
        "categories": categories,
        "articles": faqs
    })

@stats_bp.route('/api/contacts', methods=['GET'])
def get_contacts():
    return jsonify({
        "success": True,
        "data": Config.EMERGENCY_CONTACTS
    })
