from flask import Blueprint, request, jsonify, session, redirect, url_for, render_template, flash, current_app
from models.user import User
from models.service_request import ServiceRequest
from models.helper import Helper
from models.feedback import Feedback
from models.complaint import Complaint
from functools import wraps
import os
from rate_limiter import limiter

user_bp = Blueprint('user', __name__, url_prefix='/user')

# Middleware to check if user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_type' not in session or session['user_type'] != 'user':
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@user_bp.route('/dashboard')
@login_required
def dashboard():
    user_id = session.get('user_id')
    
    if not user_id:
        flash('Please log in to access your dashboard.', 'danger')
        return redirect(url_for('auth.login'))
    
    try:
        # Get user information
        user = User.get_by_id(user_id)
        if not user:
            flash('User not found.', 'danger')
            return redirect(url_for('auth.login'))
        
        # Get service requests for this user
        service_requests = ServiceRequest.get_by_user_id(user_id)
        
        # Calculate stats
        total_requests = len(service_requests)
        pending_requests = len([req for req in service_requests if req.status in ['open', 'assigned']])
        completed_requests = len([req for req in service_requests if req.status == 'completed'])
        in_progress_requests = len([req for req in service_requests if req.status == 'in_progress'])
        
        stats = {
            'total_requests': total_requests,
            'pending_requests': pending_requests,
            'completed_requests': completed_requests,
            'in_progress_requests': in_progress_requests
        }
        
        return render_template('user/dashboard.html', 
                             service_requests=service_requests, 
                             user=user, 
                             stats=stats)
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'danger')
        return redirect(url_for('index'))

@user_bp.route('/request/new', methods=['GET', 'POST'])
@login_required
def new_request():
    if request.method == 'GET':
        # Get categories from database
        from models.database import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT name FROM categories ORDER BY name')
        categories = [row['name'] for row in cursor.fetchall()]
        conn.close()
        
        if not categories:
            # Fallback categories if none in database
            categories = ['Home Repair', 'Technology', 'Transportation', 'Cleaning', 'Cooking', 'Gardening', 'Companionship', 'Education']
        
        return render_template('user/new_request.html', categories=categories)
    
    # Handle form submission
    if request.method == 'POST':
        user_id = session.get('user_id')
        
        # Get form data
        title = request.form.get('title', '').strip()
        category = request.form.get('category', '').strip()
        description = request.form.get('description', '').strip()
        deadline = request.form.get('deadline', '').strip()
        
        # Validate form data
        if not title or not category or not description:
            flash('Please fill out all required fields', 'danger')
            # Get categories again for form
            from models.database import get_db_connection
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT name FROM categories ORDER BY name')
            categories = [row['name'] for row in cursor.fetchall()]
            conn.close()
            return render_template('user/new_request.html', categories=categories)
        
        try:
            # Create service request in database
            request_id = ServiceRequest.create(
                user_id=user_id,
                category=category,
                title=title,
                description=description,
                deadline=deadline if deadline else None
            )
            
            flash('Your service request has been created successfully!', 'success')
            return redirect(url_for('user.view_request', request_id=request_id))
            
        except Exception as e:
            flash(f'Error creating service request: {str(e)}', 'danger')
            # Get categories again for form
            from models.database import get_db_connection
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT name FROM categories ORDER BY name')
            categories = [row['name'] for row in cursor.fetchall()]
            conn.close()
            return render_template('user/new_request.html', categories=categories)

@user_bp.route('/request/<int:request_id>')
@login_required
def view_request(request_id):
    user_id = session.get('user_id')
    
    try:
        # Get service request from database
        service_request = ServiceRequest.get_by_id(request_id)
        
        if not service_request:
            flash('Service request not found.', 'danger')
            return redirect(url_for('user.dashboard'))
        
        # Check if this request belongs to the current user
        if service_request.user_id != user_id:
            flash('You do not have permission to view this request.', 'danger')
            return redirect(url_for('user.dashboard'))
        
        # Get helper information if assigned
        helper = None
        helper_user = None
        if service_request.helper_id:
            helper = Helper.get_by_id(service_request.helper_id)
            if helper:
                helper_user = User.get_by_id(helper.user_id)
        
        # Get feedback if exists
        feedback = None
        if service_request.status == 'completed':
            feedback = Feedback.get_by_request_id(request_id)
        
        return render_template('user/view_request.html', 
                             service_request=service_request,
                             helper=helper,
                             helper_user=helper_user,
                             feedback=feedback)
                             
    except Exception as e:
        flash(f'Error loading service request: {str(e)}', 'danger')
        return redirect(url_for('user.dashboard'))

@user_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@limiter.exempt
def profile():
    # Debugging: Log the session state
    current_app.logger.info(f"Session state: {session}")

    user_id = session.get('user', {}).get('id')
    if not user_id:
        flash('You must be logged in to view your profile.', 'danger')
        return redirect(url_for('auth.login'))

    # Fetch user data from the database
    user = User.get_by_id(user_id)
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        # Validate required fields
        name = request.form.get('name')
        if not name:
            flash('Name is required.', 'danger')
            return redirect(url_for('user.profile'))

        # Update user profile in the database
        user.name = name
        user.phone = request.form.get('phone')
        user.address = request.form.get('address')
        
        # Handle profile picture upload
        if 'profile_picture' in request.files:
            profile_picture_file = request.files['profile_picture']
            if profile_picture_file.filename:
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], profile_picture_file.filename)
                profile_picture_file.save(file_path)
                user.profile_picture = file_path

        user.location = request.form.get('location')
        user.update()

        flash('Profile updated successfully!', 'success')
        return redirect(url_for('user.profile'))

    return render_template('user/profile.html', user=user.to_dict())

@user_bp.route('/request/<int:request_id>/cancel', methods=['POST'])
@login_required
def cancel_request(request_id):
    user_id = session.get('user_id')
    
    # Get service request
    service_request = ServiceRequest.get_by_id(request_id)
    
    if not service_request or service_request.user_id != user_id:
        return redirect(url_for('user.dashboard'))
    
    # Cancel service request
    service_request.update_status('cancelled')
    
    return redirect(url_for('user.dashboard'))

@user_bp.route('/request/<int:request_id>/complete', methods=['POST'])
@login_required
def complete_request(request_id):
    user_id = session.get('user_id')
    
    # Get service request
    service_request = ServiceRequest.get_by_id(request_id)
    
    if not service_request or service_request.user_id != user_id:
        return redirect(url_for('user.dashboard'))
    
    # Mark service request as completed
    service_request.update_status('completed')
    
    return redirect(url_for('user.view_request', request_id=request_id))

@user_bp.route('/request/<int:request_id>/feedback', methods=['GET', 'POST'])
@login_required
def submit_feedback(request_id):
    user_id = session['user']['id']
    
    # Get service request
    service_request = ServiceRequest.get_by_id(request_id)
    
    if not service_request or service_request.user_id != user_id or service_request.status != 'completed':
        return redirect(url_for('user.dashboard'))
    
    # Check if feedback already exists
    existing_feedback = Feedback.get_by_service_request_id(request_id)
    if existing_feedback:
        return redirect(url_for('user.view_request', request_id=request_id))
    
    if request.method == 'GET':
        return render_template('user/feedback.html', service_request=service_request)
    
    data = request.form
    
    try:
        # Create feedback
        Feedback.create(
            user_id=user_id,
            helper_id=service_request.helper_id,
            service_request_id=request_id,
            rating=int(data['rating']),
            review=data.get('review')
        )
        
        return redirect(url_for('user.view_request', request_id=request_id))
    
    except Exception as e:
        return render_template('user/feedback.html', service_request=service_request, error=str(e))

@user_bp.route('/request/<int:request_id>/complaint', methods=['GET', 'POST'])
@login_required
def submit_complaint(request_id):
    user_id = session['user']['id']
    
    # Get service request
    service_request = ServiceRequest.get_by_id(request_id)
    
    if not service_request or service_request.user_id != user_id or not service_request.helper_id:
        return redirect(url_for('user.dashboard'))
    
    if request.method == 'GET':
        return render_template('user/complaint.html', service_request=service_request)
    
    data = request.form
    
    try:
        # Create complaint
        Complaint.create(
            user_id=user_id,
            helper_id=service_request.helper_id,
            service_request_id=request_id,
            description=data['description']
        )
        
        return redirect(url_for('user.view_request', request_id=request_id))
    
    except Exception as e:
        return render_template('user/complaint.html', service_request=service_request, error=str(e))

@user_bp.route('/find-helpers')
@login_required
def find_helpers():
    # Get all verified helpers
    helpers = Helper.get_all(verified_only=True)
    
    helper_profiles = []
    for helper in helpers:
        user = User.get_by_id(helper.user_id)
        if user:
            helper_profiles.append({
                'helper': helper,
                'user': user
            })
    
    return render_template('user/find_helpers.html', helper_profiles=helper_profiles)

@user_bp.route('/helper/<int:helper_id>')
@login_required
def view_helper(helper_id):
    # Get helper
    helper = Helper.get_by_id(helper_id)
    
    if not helper or not helper.verified:
        return redirect(url_for('user.find_helpers'))
    
    # Get helper user information
    helper_user = User.get_by_id(helper.user_id)
    
    # Get helper feedback
    feedback_list = Feedback.get_by_helper_id(helper_id)
    
    return render_template('user/view_helper.html', 
                           helper=helper, 
                           helper_user=helper_user,
                           feedback_list=feedback_list)

@user_bp.route('/my-requests')
@login_required
def my_requests():
    """Display all service requests for the current user"""
    user_id = session.get('user_id')
    
    if not user_id:
        flash('Please log in to view your requests.', 'danger')
        return redirect(url_for('auth.login'))
    
    try:
        # Get all service requests for this user
        service_requests = ServiceRequest.get_by_user_id(user_id)
        
        # Get user information
        user = User.get_by_id(user_id)
        
        return render_template('user/my_requests.html', 
                             service_requests=service_requests,
                             user=user)
                             
    except Exception as e:
        flash(f'Error loading requests: {str(e)}', 'danger')
        return redirect(url_for('user.dashboard'))

@user_bp.route('/messages')
@login_required
def messages():
    """Display messages for the current user"""
    user_id = session.get('user_id')
    
    if not user_id:
        flash('Please log in to view messages.', 'danger')
        return redirect(url_for('auth.login'))
    
    try:
        # Get messages for this user (placeholder for now)
        from models.database import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT m.*, u.name as sender_name 
            FROM messages m 
            JOIN users u ON m.sender_id = u.id 
            WHERE m.receiver_id = ? 
            ORDER BY m.created_at DESC
        ''', (user_id,))
        
        messages = cursor.fetchall()
        conn.close()
        
        return render_template('user/messages.html', messages=messages)
        
    except Exception as e:
        flash(f'Error loading messages: {str(e)}', 'danger')
        return redirect(url_for('user.dashboard'))

@user_bp.route('/feedback-history')
@login_required
def feedback_history():
    """Display feedback history for the current user"""
    user_id = session.get('user_id')
    
    if not user_id:
        flash('Please log in to view feedback.', 'danger')
        return redirect(url_for('auth.login'))
    
    try:
        # Get feedback given by this user
        feedback_list = Feedback.get_by_user_id(user_id)
        
        return render_template('user/feedback_history.html', 
                             feedback_list=feedback_list)
                             
    except Exception as e:
        flash(f'Error loading feedback: {str(e)}', 'danger')
        return redirect(url_for('user.dashboard'))

@user_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """Display and update user settings"""
    user_id = session.get('user_id')
    
    if not user_id:
        flash('Please log in to access settings.', 'danger')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        try:
            # Handle settings update
            user = User.get_by_id(user_id)
            if user:
                # Update notification preferences
                notifications_enabled = request.form.get('notifications_enabled') == 'on'
                email_notifications = request.form.get('email_notifications') == 'on'
                sms_notifications = request.form.get('sms_notifications') == 'on'
                
                # For now, just show success message
                flash('Settings updated successfully!', 'success')
                
        except Exception as e:
            flash(f'Error updating settings: {str(e)}', 'danger')
    
    try:
        user = User.get_by_id(user_id)
        return render_template('user/settings.html', user=user)
        
    except Exception as e:
        flash(f'Error loading settings: {str(e)}', 'danger')
        return redirect(url_for('user.dashboard'))