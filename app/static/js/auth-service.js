/**
 * Firebase Authentication Service for Community Helper Hub
 * Handles user authentication, registration, and profile management
 */

class AuthService {
    constructor() {
        this.auth = firebase.auth();
        this.currentUser = null;
        this.userProfile = null;
        this.authStateChanged = false;

        // Set up auth state listener
        this.auth.onAuthStateChanged(user => {
            this.authStateChanged = true;
            this.currentUser = user;

            if (user) {
                this._fetchUserProfile();
                this._notifyAuthStateChange(true);
            } else {
                this.userProfile = null;
                this._notifyAuthStateChange(false);
            }
        });
    }

    // Email/Password Registration
    async registerWithEmail(email, password, name) {
        try {
            // Create the user in Firebase
            const userCredential = await this.auth.createUserWithEmailAndPassword(email, password);

            // Update display name
            await userCredential.user.updateProfile({
                displayName: name
            });

            // Create user profile in backend
            await this._createUserProfile(userCredential.user, { name });

            return {
                success: true,
                user: userCredential.user
            };
        } catch (error) {
            console.error('Registration error:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    // Email/Password Login
    async loginWithEmail(email, password) {
        try {
            const userCredential = await this.auth.signInWithEmailAndPassword(email, password);
            return {
                success: true,
                user: userCredential.user
            };
        } catch (error) {
            console.error('Login error:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    // Google Sign In
    async loginWithGoogle() {
        try {
            const provider = new firebase.auth.GoogleAuthProvider();
            provider.addScope('profile');
            provider.addScope('email');

            const userCredential = await this.auth.signInWithPopup(provider);

            // Check if this is a new user
            const isNewUser = userCredential.additionalUserInfo.isNewUser;

            if (isNewUser) {
                // Create user profile in backend for new Google users
                await this._createUserProfile(userCredential.user, {
                    name: userCredential.user.displayName
                });
            }

            return {
                success: true,
                user: userCredential.user,
                isNewUser: isNewUser
            };
        } catch (error) {
            console.error('Google sign-in error:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    // Sign Out
    async logout() {
        try {
            await this.auth.signOut();
            return { success: true };
        } catch (error) {
            console.error('Logout error:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    // Password Reset
    async sendPasswordResetEmail(email) {
        try {
            await this.auth.sendPasswordResetEmail(email);
            return { success: true };
        } catch (error) {
            console.error('Password reset error:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    // Get current user
    getCurrentUser() {
        return this.currentUser;
    }

    // Get user profile
    getUserProfile() {
        return this.userProfile;
    }

    // Check if user is authenticated
    isAuthenticated() {
        return !!this.currentUser;
    }

    // Get authentication token
    async getIdToken() {
        if (!this.currentUser) return null;

        try {
            return await this.currentUser.getIdToken();
        } catch (error) {
            console.error('Error getting ID token:', error);
            return null;
        }
    }

    // Update user profile
    async updateProfile(profileData) {
        if (!this.currentUser) {
            return {
                success: false,
                error: 'User not authenticated'
            };
        }

        try {
            // Update Firebase user profile if name is provided
            if (profileData.name) {
                await this.currentUser.updateProfile({
                    displayName: profileData.name
                });
            }

            // Update backend profile
            const token = await this.getIdToken();

            const response = await fetch('/api/user/profile', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(profileData)
            });

            const data = await response.json();

            if (data.success) {
                // Refresh user profile
                await this._fetchUserProfile();

                return {
                    success: true,
                    profile: this.userProfile
                };
            } else {
                return {
                    success: false,
                    error: data.error || 'Failed to update profile'
                };
            }
        } catch (error) {
            console.error('Profile update error:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    // Private: Create user profile in backend
    async _createUserProfile(user, profileData) {
        try {
            const token = await user.getIdToken();

            const response = await fetch('/api/user/create-profile', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    uid: user.uid,
                    email: user.email,
                    name: profileData.name || user.displayName,
                    photoURL: user.photoURL || null
                })
            });

            return await response.json();
        } catch (error) {
            console.error('Error creating user profile:', error);
            throw error;
        }
    }

    // Private: Fetch user profile from backend
    async _fetchUserProfile() {
        if (!this.currentUser) return null;

        try {
            const token = await this.getIdToken();

            const response = await fetch('/api/user/profile', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            const data = await response.json();

            if (data.success) {
                this.userProfile = data.profile;
            } else {
                console.error('Error fetching user profile:', data.error);
            }

            return this.userProfile;
        } catch (error) {
            console.error('Error fetching user profile:', error);
            return null;
        }
    }

    // Private: Notify auth state change
    _notifyAuthStateChange(isAuthenticated) {
        // Dispatch custom event
        const event = new CustomEvent('authStateChanged', {
            detail: {
                isAuthenticated,
                user: this.currentUser,
                profile: this.userProfile
            }
        });

        document.dispatchEvent(event);
    }
}

// Initialize auth service
const authService = new AuthService();

// Add event listener for auth forms
document.addEventListener('DOMContentLoaded', () => {
    // Login form - DO NOT intercept; let the form POST to the Flask backend
    // which handles authentication, session creation, and role-based redirect.
    // The previous client-side Firebase auth bypass was causing helpers to land
    // on '/dashboard' (which doesn't exist) instead of '/helper/dashboard'.

    // Registration form - DO NOT intercept; let the form POST to the Flask backend
    // which handles registration and redirects to the login page.

    // Google sign-in buttons - DO NOT intercept; let the Flask backend handle auth.

    // Logout buttons
    const logoutButtons = document.querySelectorAll('.logout-button');
    logoutButtons.forEach(button => {
        button.addEventListener('click', async (e) => {
            e.preventDefault();

            await authService.logout();
            window.location.href = '/auth/logout';
        });
    });

    // Password reset form
    const passwordResetForm = document.getElementById('password-reset-form');
    if (passwordResetForm) {
        passwordResetForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const email = passwordResetForm.querySelector('[name="email"]').value;

            // Show loading state
            const submitButton = passwordResetForm.querySelector('button[type="submit"]');
            const originalText = submitButton.textContent;
            submitButton.disabled = true;
            submitButton.textContent = 'Sending...';

            const result = await authService.sendPasswordResetEmail(email);

            if (result.success) {
                // Show success message
                const successElement = passwordResetForm.querySelector('.auth-success');
                if (successElement) {
                    successElement.textContent = 'Password reset email sent. Check your inbox.';
                    successElement.style.display = 'block';
                }

                // Hide form
                passwordResetForm.querySelector('.form-fields').style.display = 'none';
            } else {
                // Show error
                const errorElement = passwordResetForm.querySelector('.auth-error');
                if (errorElement) {
                    errorElement.textContent = result.error;
                    errorElement.style.display = 'block';
                }

                // Reset button
                submitButton.disabled = false;
                submitButton.textContent = originalText;
            }
        });
    }
});