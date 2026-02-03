from flask import Blueprint, request, jsonify, session, redirect, url_for, render_template, flash
from functools import wraps
from models.user import User
from models.helper import Helper
from models.service_request import ServiceRequest
from models.feedback import Feedback
from models.verification import Verification
import os
import uuid

helper_bp = Blueprint('helper', __name__, url_prefix='/helper')

# Middleware to check if user is logged in and is a helper
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_type' not in session or session['user_type'] != 'helper':
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@helper_bp.route('/dashboard')
@login_required
def dashboard():
    user_id = session.get('user_id')
    
    if not user_id:
        flash('Please log in to access your dashboard.', 'danger')
        return redirect(url_for('auth.login'))
    
    try:
        # Get helper profile
        helper = Helper.get_by_user_id(user_id)
        if not helper:
            flash('Helper profile not found.', 'danger')
            return redirect(url_for('auth.login'))
        
        # Get user information
        user = User.get_by_id(user_id)
        
        # Get service requests assigned to this helper
        assigned_requests = ServiceRequest.get_by_helper_id(helper.id)
        
        # Get feedback for this helper
        feedback_list = Feedback.get_by_helper_id(helper.id)
        
        # Get verification status
        verification = Verification.get_by_helper_id(helper.id)
        verification_status = verification.status if verification else "Pending"
        
        # Calculate stats
        total_jobs = len(assigned_requests)
        completed_jobs = len([req for req in assigned_requests if req.status == 'completed'])
        in_progress_jobs = len([req for req in assigned_requests if req.status == 'in_progress'])
        
        stats = {
            'total_jobs': total_jobs,
            'completed_jobs': completed_jobs,
            'in_progress_jobs': in_progress_jobs,
            'rating': helper.rating,
            'total_ratings': helper.total_ratings
        }
        
        return render_template('helper/dashboard.html', 
                             helper=helper,
                             user=user,
                             service_requests=assigned_requests,
                             feedback_list=feedback_list,
                             verification_status=verification_status,
                             stats=stats)
                             
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'danger')
        return redirect(url_for('index'))

@helper_bp.route('/requests')
@login_required
def requests():
    user_id = session.get('user_id')
    
    try:
        # Get helper profile
        helper = Helper.get_by_user_id(user_id)
        if not helper:
            flash('Helper profile not found.', 'danger')
            return redirect(url_for('auth.login'))
        
        # Check if helper is verified
        verification = Verification.get_by_helper_id(helper.id)
        verification_status = verification.status if verification else "Pending"
        
        if verification_status != "Verified":
            flash('You must be verified before you can view service requests.', 'warning')
            return redirect(url_for('helper.verification'))
        
        # Get available service requests (not assigned or assigned to this helper)
        available_requests = ServiceRequest.get_available_for_helper(helper.id)
        
        # Get helper's assigned requests
        assigned_requests = ServiceRequest.get_by_helper_id(helper.id)
        
        return render_template('helper/requests.html', 
                             available_requests=available_requests,
                             assigned_requests=assigned_requests,
                             helper=helper)
                             
    except Exception as e:
        flash(f'Error loading requests: {str(e)}', 'danger')
        return redirect(url_for('helper.dashboard'))

@helper_bp.route('/request/<int:request_id>')
@login_required
def view_request(request_id):
    # Get service request
    service_request = ServiceRequest.get_by_id(request_id)
    
    if not service_request:
        return redirect(url_for('helper.available_requests'))
    
    # Get user information
    user = User.get_by_id(service_request.user_id)
    
    # Check if helper is assigned to this request
    user_id = session['user']['id']
    helper = Helper.get_by_user_id(user_id)
    is_assigned = helper and service_request.helper_id == helper.id
    
    return render_template('helper/view_request.html', 
                           service_request=service_request, 
                           user=user,
                           is_assigned=is_assigned)

@helper_bp.route('/request/<int:request_id>/accept', methods=['POST'])
@login_required
def accept_request(request_id):
    user_id = session['user']['id']
    
    # Get helper profile
    helper = Helper.get_by_user_id(user_id)
    
    if not helper:
        return redirect(url_for('index'))
    
    # Get service request
    service_request = ServiceRequest.get_by_id(request_id)
    
    if not service_request or service_request.status != 'open':
        return redirect(url_for('helper.available_requests'))
    
    # Assign helper to service request
    service_request.assign_helper(helper.id)
    
    return redirect(url_for('helper.dashboard'))

@helper_bp.route('/request/<int:request_id>/start', methods=['POST'])
@login_required
def start_request(request_id):
    user_id = session['user']['id']
    
    # Get helper profile
    helper = Helper.get_by_user_id(user_id)
    
    if not helper:
        return redirect(url_for('index'))
    
    # Get service request
    service_request = ServiceRequest.get_by_id(request_id)
    
    if not service_request or service_request.helper_id != helper.id or service_request.status != 'assigned':
        return redirect(url_for('helper.dashboard'))
    
    # Update service request status
    service_request.update_status('in_progress')
    
    return redirect(url_for('helper.view_request', request_id=request_id))

@helper_bp.route('/request/<int:request_id>/complete', methods=['POST'])
@login_required
def complete_request(request_id):
    user_id = session['user']['id']
    
    # Get helper profile
    helper = Helper.get_by_user_id(user_id)
    
    if not helper:
        return redirect(url_for('index'))
    
    # Get service request
    service_request = ServiceRequest.get_by_id(request_id)
    
    if not service_request or service_request.helper_id != helper.id or service_request.status != 'in_progress':
        return redirect(url_for('helper.dashboard'))
    
    # Update service request status
    service_request.update_status('completed')
    
    return redirect(url_for('helper.dashboard'))

@helper_bp.route('/profile')
@login_required
def profile():
    user_id = session['user']['id']
    
    # Get user information
    user = User.get_by_id(user_id)
    
    # Get helper profile
    helper = Helper.get_by_user_id(user_id)
    
    if not helper:
        return redirect(url_for('index'))
    
    # Get helper's feedback
    feedback_list = Feedback.get_by_helper_id(helper.id)
    
    return render_template('helper/profile.html', 
                           user=user, 
                           helper=helper,
                           feedback_list=feedback_list)

@helper_bp.route('/update-profile', methods=['POST'])
@login_required
def update_profile():
    user_id = session['user']['id']
    
    # Get user information
    user = User.get_by_id(user_id)
    
    # Get helper profile
    helper = Helper.get_by_user_id(user_id)
    
    if not helper:
        return redirect(url_for('index'))
    
    data = request.form
    
    # Update user information
    user.name = data['name']
    user.phone = data.get('phone')
    user.address = data.get('address')
    user.update()
    
    # Update helper information
    helper.skills = data.get('skills', '')
    helper.experience = data.get('experience')
    helper.availability = data.get('availability')
    helper.update()
    
    # Update session data
    session['user']['name'] = user.name
    
    return redirect(url_for('helper.profile'))

@helper_bp.route('/verification')
@login_required
def verification():
    status = request.args.get('status', 'none')
    
    # Mock helper data for testing
    helper = {
        'id': session.get('user_id', 1),
        'user_id': session.get('user_id', 1),
        'name': session.get('user', {}).get('name', 'Test Helper'),
        'verified': False
    }
    
    # Mock verification data for testing
    verification = None
    if status != 'none':
        verification = {
            'id': 1,
            'helper_id': helper['id'],
            'status': status,
            'documents': {
                'id_document': 'uploads/verification/id_123456.jpg',
                'certificate': 'uploads/verification/cert_123456.pdf'
            },
            'created_at': '2023-06-01 10:00:00',
            'notes': 'Your documents have been reviewed.'
        }
    else:
        verification = {
            'id': 1,
            'helper_id': helper['id'],
            'status': status,
            'documents': [],
            'created_at': '2023-09-13 10:00:00'
        }
    
    return render_template('helper/verification.html', 
                            helper=helper,
                            verification=verification,
                            status=status)

@helper_bp.route('/verification/submit', methods=['POST'])
@login_required
def submit_verification():
    # For testing purposes, we'll use a simplified approach
    
    # Check if files were uploaded (simplified check)
    if 'id_proof' not in request.files or 'certificate' not in request.files:
        flash('Please upload all required documents', 'danger')
        return redirect(url_for('helper.verification'))
    
    # Flash success message for testing
    flash('Your verification documents have been submitted and will be reviewed soon', 'success')
    
    # Redirect to verification page with pending status for testing
    return redirect(url_for('helper.verification', status='pending'))
