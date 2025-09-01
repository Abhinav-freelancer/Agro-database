import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import './UserProfile.css';

interface UserData {
  id: string;
  username: string;
  email: string;
  full_name?: string;
  is_active: boolean;
  is_admin: boolean;
}

const UserProfile: React.FC = () => {
  const { user, token, logout } = useAuth();
  const [userData, setUserData] = useState<UserData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [editMode, setEditMode] = useState<boolean>(false);
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    current_password: '',
    new_password: '',
    confirm_password: ''
  });
  const [updateMessage, setUpdateMessage] = useState<string | null>(null);

  useEffect(() => {
    const fetchUserData = async () => {
      if (!token) return;
      
      try {
        const response = await fetch('http://localhost:8000/users/me', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (!response.ok) {
          throw new Error(`Error: ${response.status}`);
        }

        const data = await response.json();
        setUserData(data);
        setFormData(prev => ({
          ...prev,
          full_name: data.full_name || '',
          email: data.email || ''
        }));
        setLoading(false);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An unknown error occurred');
        setLoading(false);
      }
    };

    fetchUserData();
  }, [token]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setUpdateMessage(null);
    
    // Validate passwords if trying to change password
    if (formData.new_password) {
      if (!formData.current_password) {
        setError('Current password is required to set a new password');
        return;
      }
      if (formData.new_password !== formData.confirm_password) {
        setError('New passwords do not match');
        return;
      }
    }

    try {
      // Prepare update data
      const updateData: Record<string, string> = {};
      if (formData.full_name !== userData?.full_name) {
        updateData.full_name = formData.full_name;
      }
      if (formData.email !== userData?.email) {
        updateData.email = formData.email;
      }
      if (formData.new_password) {
        updateData.current_password = formData.current_password;
        updateData.new_password = formData.new_password;
      }

      // Only send request if there are changes
      if (Object.keys(updateData).length > 0) {
        const response = await fetch('http://localhost:8000/users/me', {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify(updateData)
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || `Error: ${response.status}`);
        }

        const updatedUser = await response.json();
        setUserData(updatedUser);
        setUpdateMessage('Profile updated successfully');
        
        // Clear password fields
        setFormData(prev => ({
          ...prev,
          current_password: '',
          new_password: '',
          confirm_password: ''
        }));
      } else {
        setUpdateMessage('No changes to update');
      }
      
      setEditMode(false);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
    }
  };

  if (loading) {
    return <div className="profile-loading">Loading profile...</div>;
  }

  if (error && !editMode) {
    return <div className="profile-error">Error: {error}</div>;
  }

  return (
    <div className="user-profile">
      <h1>User Profile</h1>
      
      {!editMode ? (
        <div className="profile-view">
          <div className="profile-card">
            <div className="profile-header">
              <div className="profile-avatar">
                {userData?.username.charAt(0).toUpperCase()}
              </div>
              <div className="profile-title">
                <h2>{userData?.username}</h2>
                <span className={`role-badge ${userData?.is_admin ? 'admin' : 'user'}`}>
                  {userData?.is_admin ? 'Administrator' : 'User'}
                </span>
              </div>
            </div>
            
            <div className="profile-details">
              <div className="detail-item">
                <span className="detail-label">Full Name:</span>
                <span className="detail-value">{userData?.full_name || 'Not provided'}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Email:</span>
                <span className="detail-value">{userData?.email}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Account Status:</span>
                <span className={`status-badge ${userData?.is_active ? 'active' : 'inactive'}`}>
                  {userData?.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
            </div>
            
            {updateMessage && (
              <div className="update-message success">{updateMessage}</div>
            )}
            
            <div className="profile-actions">
              <button 
                className="edit-profile-btn"
                onClick={() => setEditMode(true)}
              >
                Edit Profile
              </button>
              <button 
                className="logout-btn"
                onClick={logout}
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      ) : (
        <div className="profile-edit">
          <div className="profile-card">
            <h2>Edit Profile</h2>
            
            {error && <div className="update-message error">{error}</div>}
            
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label htmlFor="username">Username</label>
                <input 
                  type="text" 
                  id="username" 
                  value={userData?.username || ''} 
                  disabled 
                />
                <small>Username cannot be changed</small>
              </div>
              
              <div className="form-group">
                <label htmlFor="full_name">Full Name</label>
                <input 
                  type="text" 
                  id="full_name" 
                  name="full_name" 
                  value={formData.full_name} 
                  onChange={handleInputChange} 
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="email">Email</label>
                <input 
                  type="email" 
                  id="email" 
                  name="email" 
                  value={formData.email} 
                  onChange={handleInputChange} 
                  required 
                />
              </div>
              
              <h3>Change Password</h3>
              <div className="form-group">
                <label htmlFor="current_password">Current Password</label>
                <input 
                  type="password" 
                  id="current_password" 
                  name="current_password" 
                  value={formData.current_password} 
                  onChange={handleInputChange} 
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="new_password">New Password</label>
                <input 
                  type="password" 
                  id="new_password" 
                  name="new_password" 
                  value={formData.new_password} 
                  onChange={handleInputChange} 
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="confirm_password">Confirm New Password</label>
                <input 
                  type="password" 
                  id="confirm_password" 
                  name="confirm_password" 
                  value={formData.confirm_password} 
                  onChange={handleInputChange} 
                />
              </div>
              
              <div className="form-actions">
                <button type="submit" className="save-btn">Save Changes</button>
                <button 
                  type="button" 
                  className="cancel-btn" 
                  onClick={() => {
                    setEditMode(false);
                    setError(null);
                    // Reset form data to current user data
                    setFormData(prev => ({
                      ...prev,
                      full_name: userData?.full_name || '',
                      email: userData?.email || '',
                      current_password: '',
                      new_password: '',
                      confirm_password: ''
                    }));
                  }}
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default UserProfile;