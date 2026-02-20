from flask import Blueprint, request, render_template, redirect, url_for, flash, session
from ..models.user import User
from ..models.helper import Helper
from ..models.admin import Admin
from functools import wraps
import logging

logger = logging.getLogger(__name__)
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form data
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        name = request.form.get('name', '').strip()
        user_type = request.form.get('user_type', 'user').strip()
        
        logger.info(f"Processing registration for {email} as {user_type}")
        
        # Validate required fields
        if not email or not password or not name:
            flash('Please fill in all required fields.', 'danger')
            return render_template('auth/register.html')
        
        # Validate password length
        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'danger')
            return render_template('auth/register.html')
        
        # Validate user type
        if user_type not in ['user', 'helper']:
            flash('Invalid user type selected.', 'danger')
            return render_template('auth/register.html')
        
        try:
            # Create user
            user_id = User.create(
                email=email,
                name=name,
                password=password,
                user_type=user_type
            )
            
            logger.info(f"Created user with ID {user_id}")
            
            # If user is a helper, create helper profile
            if user_type == 'helper':
                skills = request.form.get('skills', '').strip()
                experience = request.form.get('experience', '0').strip()
                availability = request.form.get('availability', '').strip()
                
                if not skills or not availability:
                    flash('Please provide your skills and availability.', 'danger')
                    return render_template('auth/register.html')
                
                helper_id = Helper.create(
                    user_id=user_id,
                    skills=skills,
                    experience=experience,
                    availability=availability
                )
                logger.info(f"Created helper profile with ID {helper_id}")
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
            
        except ValueError as e:
            logger.warning(f"Validation error during registration: {str(e)}")
            flash(str(e), 'danger')
        except Exception as e:
            logger.error(f"Unexpected error during registration: {str(e)}", exc_info=True)
            flash(f"An unexpected error occurred: {str(e)}", 'danger')
    
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.get_by_email(email)
        
        if user and user.verify_password(password):
            session['user_id'] = user.id
            session['user_type'] = user.user_type
            session['user_name'] = user.name
            session['user'] = {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'user_type': user.user_type
            }
            session.permanent = True
            
            flash(f'Welcome back, {user.name}!', 'success')
            
            if user.user_type == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif user.user_type == 'helper':
                return redirect(url_for('helper.dashboard'))
            else:
                return redirect(url_for('user.dashboard'))
        
        flash('Invalid email or password.', 'danger')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@auth_bp.route('/profile')
def profile():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    
    user = User.get_by_id(session['user']['id'])
    
    # If user is a helper, get helper profile
    helper_profile = None
    if user.user_type == 'helper':
        helper_profile = Helper.get_by_user_id(user.id)
    
    return render_template('auth/profile.html', user=user, helper_profile=helper_profile)

@auth_bp.route('/update-profile', methods=['POST'])
def update_profile():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    
    data = request.form
    user = User.get_by_id(session['user']['id'])
    
    # Update user information
    user.name = data['name']
    user.phone = data.get('phone')
    user.address = data.get('address')
    user.update()
    
    # If user is a helper, update helper profile
    if user.user_type == 'helper':
        helper = Helper.get_by_user_id(user.id)
        if helper:
            helper.skills = data.get('skills', '')
            helper.experience = data.get('experience')
            helper.availability = data.get('availability')
            helper.update()
    
    # Update session data
    session['user']['name'] = user.name
    
    return redirect(url_for('auth.profile'))