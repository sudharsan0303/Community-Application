from flask import Blueprint, request, jsonify, session, redirect, url_for, render_template, flash, current_app
from functools import wraps
from ..models.user import User
from ..models.helper import Helper
from ..models.service_request import ServiceRequest
from ..models.feedback import Feedback
from ..models.verification import Verification
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

@helper_bp.route('/complete-profile', methods=['GET', 'POST'])
@login_required
def complete_profile():
    user_id = session.get('user_id')
    user = User.get_by_id(user_id)
    
    if request.method == 'GET':
        return render_template('helper/complete_profile.html', user=user)
    
    # Handle form submission
    if request.method == 'POST':
        skills = request.form.get('skills', '').strip()
        experience = request.form.get('experience', '0').strip()
        availability = request.form.get('availability', '').strip()
    
        if not skills:
            flash('Skills are required.', 'danger')
            return render_template('helper/complete_profile.html', user=user)
            
        if not availability:
            flash('Availability is required.', 'danger')
            return render_template('helper/complete_profile.html', user=user)
        
        try:
            Helper.create(
                user_id=user_id,
                skills=skills,
                experience=experience,
                availability=availability
            )
            flash('Profile completed successfully! Welcome to your dashboard.', 'success')
            return redirect(url_for('helper.dashboard'))
        except Exception as e:
            flash(f'Error creating profile: {str(e)}', 'danger')
            return render_template('helper/complete_profile.html', user=user)

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
            flash('Please complete your profile to continue.', 'info')
            return redirect(url_for('helper.complete_profile'))
        
        # Check if helper is verified
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
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error loading helper dashboard for user {user_id}: {str(e)}", exc_info=True)
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
            flash('Please complete your profile to continue.', 'info')
            return redirect(url_for('helper.complete_profile'))
        
        # Check if helper is verified
        if not helper.verified:
            flash('You must be verified before you can view service requests.', 'warning')
            return redirect(url_for('helper.verification'))
        
        # Get available service requests (not assigned or assigned to this helper)
        available_requests = ServiceRequest.get_available_for_helper(helper.id)
        
        # Get helper's assigned requests
        assigned_requests = ServiceRequest.get_by_helper_id(helper.id)
        
        # Extract unique categories from available requests
        categories = list(set([req.category for req in available_requests if req.category]))
        categories.sort()
        
        return render_template('helper/requests.html', 
                             requests=available_requests,
                             categories=categories,
                             assigned_requests=assigned_requests,
                             helper=helper)
                             
    except Exception as e:
        print(f"Error loading requests: {str(e)}") # Debug print
        flash(f'Error loading requests: {str(e)}', 'danger')
        # Redirect to logout to prevent infinite loop (Index -> Dashboard -> Error -> Index)
        return redirect(url_for('auth.logout'))

@helper_bp.route('/request/<int:request_id>')
@login_required
def view_request(request_id):
    # Get service request
    service_request = ServiceRequest.get_by_id(request_id)
    
    if not service_request:
        return redirect(url_for('helper.requests'))
    
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
        return redirect(url_for('auth.logout'))
    
    # Get service request
    service_request = ServiceRequest.get_by_id(request_id)
    
    if not service_request or service_request.status != 'open':
        return redirect(url_for('helper.requests'))
    
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
        return redirect(url_for('auth.logout'))
    
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
        return redirect(url_for('auth.logout'))
    
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
        return redirect(url_for('auth.logout'))
    
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
        return redirect(url_for('auth.logout'))
    
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
    user_id = session.get('user_id')
    status = request.args.get('status', 'none')
    
    # Get helper profile
    helper = Helper.get_by_user_id(user_id)
    if not helper:
        flash('Helper profile not found. Please contact support.', 'danger')
        return redirect(url_for('auth.logout'))
    
    # Get verification status from database
    verification = Verification.get_by_helper_id(helper.id)
    
    if verification:
        status = verification.status
        # Parse documents if they are stored as comma-separated string
        if verification.document_path:
            verification.documents = verification.document_path.split(',')
    
    return render_template('helper/verification.html', 
                            helper=helper,
                            verification=verification,
                            status=status)

@helper_bp.route('/verification/submit', methods=['POST'])
@login_required
def submit_verification():
    user_id = session.get('user_id')
    
    # Get helper profile
    helper = Helper.get_by_user_id(user_id)
    if not helper:
        flash('Helper profile not found. Please contact support.', 'danger')
        return redirect(url_for('auth.logout'))

    # Check if files were uploaded
    if 'id_proof' not in request.files or 'certificate' not in request.files:
        flash('Please upload all required documents', 'danger')
        return redirect(url_for('helper.verification'))
    
    id_proof = request.files['id_proof']
    certificate = request.files['certificate']
    
    if id_proof.filename == '' or certificate.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('helper.verification'))

    try:
        # Create uploads directory if it doesn't exist
        upload_dir = os.path.join(current_app.static_folder, 'uploads', 'verifications')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save files
        id_filename = f"id_{helper.id}_{str(uuid.uuid4())[:8]}_{id_proof.filename}"
        cert_filename = f"cert_{helper.id}_{str(uuid.uuid4())[:8]}_{certificate.filename}"
        
        id_proof.save(os.path.join(upload_dir, id_filename))
        certificate.save(os.path.join(upload_dir, cert_filename))
        
        # Create verification record
        document_path = f"{id_filename},{cert_filename}"
        Verification.create(
            helper_id=helper.id,
            document_type="ID,Certificate",
            document_path=document_path
        )
        
        flash('Your verification documents have been submitted and will be reviewed soon', 'success')
        return redirect(url_for('helper.verification'))
        
    except Exception as e:
        flash(f'Error submitting verification: {str(e)}', 'danger')
        return redirect(url_for('helper.verification'))
