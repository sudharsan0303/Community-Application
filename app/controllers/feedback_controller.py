from flask import Blueprint, request, jsonify, session, redirect, url_for, render_template
from ..models.user import User
from ..models.helper import Helper
from ..models.service_request import ServiceRequest
from ..models.feedback import Feedback
from ..models.complaint import Complaint

feedback_bp = Blueprint('feedback', __name__, url_prefix='/feedback')

# Middleware to check if user is logged in
def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@feedback_bp.route('/helper/<int:helper_id>')
@login_required
def helper_feedback(helper_id):
    # Get helper
    helper = Helper.get_by_id(helper_id)
    
    if not helper:
        return redirect(url_for('index'))
    
    # Get helper user information
    helper_user = User.get_by_id(helper.user_id)
    
    # Get helper feedback
    feedback_list = Feedback.get_by_helper_id(helper_id)
    
    # Get user information for each feedback
    feedback_with_users = []
    for feedback in feedback_list:
        user = User.get_by_id(feedback.user_id)
        if user:
            feedback_with_users.append({
                'feedback': feedback,
                'user': user
            })
    
    return render_template('feedback/helper_feedback.html', 
                           helper=helper, 
                           helper_user=helper_user,
                           feedback_list=feedback_with_users)

@feedback_bp.route('/submit/<int:request_id>', methods=['GET', 'POST'])
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
        return render_template('feedback/submit.html', service_request=service_request)
    
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
        return render_template('feedback/submit.html', service_request=service_request, error=str(e))

@feedback_bp.route('/complaint/<int:request_id>', methods=['GET', 'POST'])
@login_required
def submit_complaint(request_id):
    user_id = session['user']['id']
    
    # Get service request
    service_request = ServiceRequest.get_by_id(request_id)
    
    if not service_request or service_request.user_id != user_id or not service_request.helper_id:
        return redirect(url_for('user.dashboard'))
    
    if request.method == 'GET':
        return render_template('feedback/complaint.html', service_request=service_request)
    
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
        return render_template('feedback/complaint.html', service_request=service_request, error=str(e))

@feedback_bp.route('/view-complaints')
@login_required
def view_complaints():
    user_id = session['user']['id']
    
    # Get user's complaints
    complaints = Complaint.get_by_user_id(user_id)
    
    # Get helper information for each complaint
    complaints_with_details = []
    for complaint in complaints:
        helper = Helper.get_by_id(complaint.helper_id)
        helper_user = None
        if helper:
            helper_user = User.get_by_id(helper.user_id)
        
        service_request = ServiceRequest.get_by_id(complaint.service_request_id)
        
        complaints_with_details.append({
            'complaint': complaint,
            'helper': helper,
            'helper_user': helper_user,
            'service_request': service_request
        })
    
    return render_template('feedback/view_complaints.html', complaints=complaints_with_details)