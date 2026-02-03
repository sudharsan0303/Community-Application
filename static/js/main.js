/**
 * Main JavaScript for Community Helper Hub
 */

document.addEventListener('DOMContentLoaded', function() {
    // Mobile menu toggle
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    const navLinks = document.querySelector('.nav-links');
    
    if (mobileMenuToggle) {
        mobileMenuToggle.addEventListener('click', function() {
            navLinks.classList.toggle('active');
        });
    }
    
    // Close alerts
    const closeAlerts = document.querySelectorAll('.close-alert');
    
    closeAlerts.forEach(function(closeAlert) {
        closeAlert.addEventListener('click', function() {
            const alert = this.parentElement;
            alert.style.opacity = '0';
            setTimeout(function() {
                alert.style.display = 'none';
            }, 300);
        });
    });
    
    // Enhanced Star rating functionality with animations
    const starRatings = document.querySelectorAll('.star-rating');
    
    starRatings.forEach(function(starRating) {
        const stars = starRating.querySelectorAll('i');
        const ratingInput = starRating.nextElementSibling;
        const ratingText = starRating.parentElement.querySelector('.rating-text');
        const ratingLabels = ['Poor', 'Fair', 'Good', 'Very Good', 'Excellent'];
        let currentRating = ratingInput ? parseInt(ratingInput.value) : 0;
        
        // Create rating text element if it doesn't exist
        if (!ratingText && starRating.parentElement) {
            const newRatingText = document.createElement('div');
            newRatingText.className = 'rating-text';
            starRating.parentElement.appendChild(newRatingText);
        }
        
        // Function to update stars visual state
        const updateStars = (rating, hoverMode = false) => {
            stars.forEach((s, i) => {
                // Remove all classes first
                s.classList.remove('active', 'inactive', 'pulse');
                
                // Add appropriate class
                if (i < rating) {
                    s.classList.add('active');
                    // Add pulse animation when clicked, not on hover
                    if (!hoverMode && rating === i + 1) {
                        s.classList.add('pulse');
                    }
                } else {
                    s.classList.add('inactive');
                }
                
                // Add delay to animation for cascade effect
                s.style.animationDelay = `${i * 50}ms`;
            });
            
            // Update rating text if it exists
            const ratingTextElement = starRating.parentElement.querySelector('.rating-text');
            if (ratingTextElement && rating > 0) {
                ratingTextElement.textContent = ratingLabels[rating - 1];
                ratingTextElement.style.opacity = '1';
            } else if (ratingTextElement) {
                ratingTextElement.style.opacity = '0';
            }
        };
        
        // Set initial state
        updateStars(currentRating);
        
        // Add events to each star
        stars.forEach((star, index) => {
            // Hover effect
            star.addEventListener('mouseenter', () => {
                updateStars(index + 1, true);
            });
            
            // Restore to current rating when mouse leaves the container
            starRating.addEventListener('mouseleave', () => {
                updateStars(currentRating);
            });
            
            // Click event
            star.addEventListener('click', () => {
                currentRating = index + 1;
                
                // Update input value
                if (ratingInput) {
                    ratingInput.value = currentRating;
                    
                    // Trigger change event on the input
                    const event = new Event('change', { bubbles: true });
                    ratingInput.dispatchEvent(event);
                }
                
                // Update stars with animation
                updateStars(currentRating);
            });
        });
    });
    
    // Google Sign-In
    const googleSignInButtons = document.querySelectorAll('.google-signin-button');
    
    googleSignInButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const provider = new firebase.auth.GoogleAuthProvider();
            
            firebase.auth().signInWithPopup(provider)
                .then(function(result) {
                    // Get ID token
                    return result.user.getIdToken();
                })
                .then(function(idToken) {
                    // Send ID token to backend
                    return fetch('/auth/google-signin', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ idToken: idToken })
                    });
                })
                .then(function(response) {
                    return response.json();
                })
                .then(function(data) {
                    if (data.success) {
                        window.location.href = data.redirect;
                    } else {
                        console.error('Google sign-in failed:', data.error);
                    }
                })
                .catch(function(error) {
                    console.error('Google sign-in error:', error);
                });
        });
    });
});