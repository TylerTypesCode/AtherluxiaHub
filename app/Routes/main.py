from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('main/index.html')

@main_bp.route('/about')
def about():
    return render_template('main/about.html')

@main_bp.route('/pricing')
def pricing():
    return render_template('main/pricing.html')

@main_bp.route('/contact')
def contact():
    return render_template('main/contact.html')
