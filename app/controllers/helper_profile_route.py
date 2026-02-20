@helper_bp.route('/complete-profile', methods=['GET', 'POST'])
@login_required
def complete_profile():
    user_id = session.get('user_id')
    user = User.get_by_id(user_id)
    
    if request.method == 'GET':
        return render_template('helper/complete_profile.html', user=user)
    
    # Handle form submission
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
