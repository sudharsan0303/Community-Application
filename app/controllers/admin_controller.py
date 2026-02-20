from flask import Blueprint, request, jsonify, session, redirect, url_for, render_template, flash
from ..models.user import User
from ..models.helper import Helper
from ..models.service_request import ServiceRequest
from ..models.feedback import Feedback
from ..models.complaint import Complaint
from ..models.verification import Verification
from functools import wraps

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Middleware to check if user is logged in and is an admin
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_type' not in session or session['user_type'] != 'admin':
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    try:
        from ..models.database import get_db_connection
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get user count
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE user_type = 'user'")
        user_count = cursor.fetchone()['count']
        
        # Get helper count
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE user_type = 'helper'")
        helper_count = cursor.fetchone()['count']
        
        # Get verified helper count
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM helpers h 
            WHERE h.verified = 1
        """)
        verified_helper_count = cursor.fetchone()['count']
        
        # Get service request count
        cursor.execute("SELECT COUNT(*) as count FROM service_requests")
        service_request_count = cursor.fetchone()['count']
        
        # Get pending complaint count
        cursor.execute("SELECT COUNT(*) as count FROM complaints WHERE status = 'Pending'")
        pending_complaint_count = cursor.fetchone()['count']
        
        # Get pending verification count
        cursor.execute("SELECT COUNT(*) as count FROM verifications WHERE status = 'Pending'")
        pending_verification_count = cursor.fetchone()['count']
        
        conn.close()
        
        return render_template('admin/dashboard.html',
                             user_count=user_count,
                             helper_count=helper_count,
                             verified_helper_count=verified_helper_count,
                             service_request_count=service_request_count,
                             pending_complaint_count=pending_complaint_count,
                             pending_verification_count=pending_verification_count)
                             
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'danger')
        return render_template('admin/dashboard.html',
                             user_count=0,
                             helper_count=0,
                             verified_helper_count=0,
                             service_request_count=0,
                             pending_complaint_count=0,
                             pending_verification_count=0)

@admin_bp.route('/users')
@login_required
def users():
    # Get all users
    users = User.get_all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/helpers')
@login_required
def helpers():
    # Get all helpers
    helpers = Helper.get_all()
    
    # Get user information for each helper
    helper_profiles = []
    for helper in helpers:
        user = User.get_by_id(helper.user_id)
        if user:
            helper_profiles.append({
                'helper': helper,
                'user': user
            })
    
    return render_template('admin/helpers.html', helper_profiles=helper_profiles)

@admin_bp.route('/verifications')
@login_required
def verifications():
    status_filter = request.args.get('status', 'Pending')
    
    # Get verifications from database
    if status_filter == 'All':
        verifications = Verification.get_all_paginated(1, 100)[0] # Simplified for now
    else:
        verifications = Verification.get_by_status(status_filter)
    
    # Get user and helper information for each verification
    verifications_with_details = []
    for verification in verifications:
        helper = Helper.get_by_id(verification.helper_id)
        if helper:
            user = User.get_by_id(helper.user_id)
            verifications_with_details.append({
                'verification': verification,
                'helper': helper,
                'user': user
            })
    
    return render_template('admin/verifications.html', 
                           verifications=verifications_with_details,
                           current_status=status_filter)

@admin_bp.route('/verification/<int:verification_id>', methods=['GET'])
@login_required
def verification_review(verification_id):
    # Get verification
    verification = Verification.get_by_id(verification_id)
    
    if not verification:
        flash('Verification request not found', 'danger')
        return redirect(url_for('admin.verifications'))
    
    # Get helper and user
    helper = Helper.get_by_id(verification.helper_id)
    if not helper:
        flash('Helper not found', 'danger')
        return redirect(url_for('admin.verifications'))
        
    user = User.get_by_id(helper.user_id)
    
    # Parse document paths
    document_paths = verification.document_path.split(',')
    documents = []
    for path in document_paths:
        if path:
            doc_type = 'ID' if 'id_' in path else 'Certificate'
            documents.append({
                'type': doc_type,
                'path': f"/static/uploads/verifications/{path}"
            })
    
    return render_template('admin/verification_review.html',
                           verification=verification,
                           helper=helper,
                           user=user,
                           documents=documents)

@admin_bp.route('/verification/<int:verification_id>/approve', methods=['POST'])
@login_required
def approve_verification(verification_id):
    admin_id = session.get('user_id')
    
    # Get verification
    verification = Verification.get_by_id(verification_id)
    if not verification:
        return redirect(url_for('admin.verifications'))
        
    # Update verification status
    Verification.update_status(verification_id, 'Approved', admin_id, 'Approved by admin')
    
    # Update helper status
    helper = Helper.get_by_id(verification.helper_id)
    if helper:
        helper.verify(True)
    
    flash(f'Verification #{verification_id} has been approved successfully', 'success')
    return redirect(url_for('admin.verifications', status='Approved'))

@admin_bp.route('/verification/<int:verification_id>/reject', methods=['POST'])
@login_required
def reject_verification(verification_id):
    admin_id = session.get('user_id')
    notes = request.form.get('notes', 'Your documents did not meet our verification requirements.')
    
    # Update verification status
    Verification.update_status(verification_id, 'Rejected', admin_id, notes)
    
    # Ensure helper is not verified
    verification.helper_id
    helper = Helper.get_by_id(verification.helper_id)
    if helper:
        helper.verify(False)
    
    flash(f'Verification #{verification_id} has been rejected', 'warning')
    return redirect(url_for('admin.verifications', status='Rejected'))

@admin_bp.route('/verification/<int:verification_id>/reopen', methods=['POST'])
@login_required
def reopen_verification(verification_id):
    admin_id = session.get('user_id')
    
    # Update verification status
    Verification.update_status(verification_id, 'Pending', admin_id, 'Reopened by admin')
    
    flash(f'Verification #{verification_id} has been reopened', 'info')
    return redirect(url_for('admin.verifications', status='Pending'))

@admin_bp.route('/requests')
@login_required
def requests():
    # Get all service requests
    conn = Helper.get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM service_requests ORDER BY created_at DESC')
    requests_data = cursor.fetchall()
    conn.close()
    
    # Get user and helper information for each request
    requests_with_details = []
    for request_data in requests_data:
        service_request = ServiceRequest(
            id=request_data['id'],
            user_id=request_data['user_id'],
            helper_id=request_data['helper_id'],
            category=request_data['category'],
            title=request_data['title'],
            description=request_data['description'],
            deadline=request_data['deadline'],
            status=request_data['status'],
            created_at=request_data['created_at'],
            updated_at=request_data['updated_at']
        )
        
        user = User.get_by_id(service_request.user_id)
        helper = None
        helper_user = None
        
        if service_request.helper_id:
            helper = Helper.get_by_id(service_request.helper_id)
            if helper:
                helper_user = User.get_by_id(helper.user_id)
        
        requests_with_details.append({
            'request': service_request,
            'user': user,
            'helper': helper,
            'helper_user': helper_user
        })
    
    return render_template('admin/requests.html', requests=requests_with_details)

@admin_bp.route('/complaints')
@login_required
def complaints():
    # Get all complaints
    conn = Helper.get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM complaints ORDER BY status ASC, created_at DESC')
    complaints_data = cursor.fetchall()
    conn.close()
    
    # Get user, helper, and service request information for each complaint
    complaints_with_details = []
    for complaint_data in complaints_data:
        complaint = Complaint(
            id=complaint_data['id'],
            user_id=complaint_data['user_id'],
            helper_id=complaint_data['helper_id'],
            service_request_id=complaint_data['service_request_id'],
            description=complaint_data['description'],
            status=complaint_data['status'],
            resolution=complaint_data['resolution'],
            created_at=complaint_data['created_at'],
            updated_at=complaint_data['updated_at']
        )
        
        user = User.get_by_id(complaint.user_id)
        helper = Helper.get_by_id(complaint.helper_id)
        helper_user = None
        if helper:
            helper_user = User.get_by_id(helper.user_id)
        service_request = ServiceRequest.get_by_id(complaint.service_request_id)
        
        complaints_with_details.append({
            'complaint': complaint,
            'user': user,
            'helper': helper,
            'helper_user': helper_user,
            'service_request': service_request
        })
    
    return render_template('admin/complaints.html', complaints=complaints_with_details)

@admin_bp.route('/complaint/<int:complaint_id>/resolve', methods=['POST'])
@login_required
def resolve_complaint(complaint_id):
    # Get complaint
    complaint = Complaint.get_by_id(complaint_id)
    
    if complaint and complaint.status == 'pending':
        # Update resolution
        resolution = request.form.get('resolution')
        complaint.resolve(resolution)
    
    return redirect(url_for('admin.complaints'))

@admin_bp.route('/feedback')
@login_required
def feedback():
    # Get all feedback
    conn = Helper.get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM feedback ORDER BY created_at DESC')
    feedback_data = cursor.fetchall()
    conn.close()
    
    # Get user, helper, and service request information for each feedback
    feedback_with_details = []
    for fb_data in feedback_data:
        feedback = Feedback(
            id=fb_data['id'],
            user_id=fb_data['user_id'],
            helper_id=fb_data['helper_id'],
            service_request_id=fb_data['service_request_id'],
            rating=fb_data['rating'],
            review=fb_data['review'],
            created_at=fb_data['created_at']
        )
        
        user = User.get_by_id(feedback.user_id)
        helper = Helper.get_by_id(feedback.helper_id)
        helper_user = None
        if helper:
            helper_user = User.get_by_id(helper.user_id)
        service_request = ServiceRequest.get_by_id(feedback.service_request_id)
        
        feedback_with_details.append({
            'feedback': feedback,
            'user': user,
            'helper': helper,
            'helper_user': helper_user,
            'service_request': service_request
        })
    
    return render_template('admin/feedback.html', feedback_list=feedback_with_details)

@admin_bp.route('/make-admin', methods=['GET', 'POST'])
@login_required
def make_admin():
    if request.method == 'GET':
        # Get all users who are not admins
        conn = Helper.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT u.* FROM users u
        LEFT JOIN admins a ON u.id = a.user_id
        WHERE a.id IS NULL
        ''')
        users_data = cursor.fetchall()
        conn.close()
        
        users = []
        for user_data in users_data:
            users.append(User(
                id=user_data['id'],
                firebase_uid=user_data['firebase_uid'],
                email=user_data['email'],
                name=user_data['name'],
                phone=user_data['phone'],
                address=user_data['address'],
                profile_picture=user_data['profile_picture'],
                user_type=user_data['user_type'],
                created_at=user_data['created_at'],
                updated_at=user_data['updated_at']
            ))
        
        return render_template('admin/make_admin.html', users=users)
    
    user_id = request.form.get('user_id')
    
    if user_id:
        # Create admin
        Admin.create(user_id=user_id)
    
    return redirect(url_for('admin.dashboard'))
