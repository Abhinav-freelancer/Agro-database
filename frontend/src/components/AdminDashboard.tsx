import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import './AdminDashboard.css';

interface User {
  id: string;
  username: string;
  email: string;
  is_active: boolean;
  is_admin: boolean;
}

const AdminDashboard: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const { token } = useAuth();

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const response = await fetch('http://localhost:8000/users/', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (!response.ok) {
          throw new Error(`Error: ${response.status}`);
        }

        const data = await response.json();
        setUsers(data);
        setLoading(false);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An unknown error occurred');
        setLoading(false);
      }
    };

    fetchUsers();
  }, [token]);

  const toggleUserStatus = async (userId: string, isActive: boolean) => {
    try {
      const response = await fetch(`http://localhost:8000/users/${userId}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ is_active: !isActive })
      });

      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }

      // Update the local state
      setUsers(users.map(user => 
        user.id === userId ? { ...user, is_active: !isActive } : user
      ));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
    }
  };

  const deleteUser = async (userId: string) => {
    if (!window.confirm('Are you sure you want to delete this user?')) {
      return;
    }

    try {
      const response = await fetch(`http://localhost:8000/users/${userId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }

      // Remove the user from the local state
      setUsers(users.filter(user => user.id !== userId));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
    }
  };

  if (loading) {
    return <div className="admin-loading">Loading users...</div>;
  }

  if (error) {
    return <div className="admin-error">Error: {error}</div>;
  }

  return (
    <div className="admin-dashboard">
      <h1>Admin Dashboard</h1>
      <div className="admin-stats">
        <div className="stat-card">
          <h3>Total Users</h3>
          <p>{users.length}</p>
        </div>
        <div className="stat-card">
          <h3>Active Users</h3>
          <p>{users.filter(user => user.is_active).length}</p>
        </div>
        <div className="stat-card">
          <h3>Admins</h3>
          <p>{users.filter(user => user.is_admin).length}</p>
        </div>
      </div>
      
      <h2>User Management</h2>
      <div className="user-table-container">
        <table className="user-table">
          <thead>
            <tr>
              <th>Username</th>
              <th>Email</th>
              <th>Status</th>
              <th>Role</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map(user => (
              <tr key={user.id}>
                <td>{user.username}</td>
                <td>{user.email}</td>
                <td>
                  <span className={`status-badge ${user.is_active ? 'active' : 'inactive'}`}>
                    {user.is_active ? 'Active' : 'Inactive'}
                  </span>
                </td>
                <td>
                  <span className={`role-badge ${user.is_admin ? 'admin' : 'user'}`}>
                    {user.is_admin ? 'Admin' : 'User'}
                  </span>
                </td>
                <td className="action-buttons">
                  <button 
                    className={user.is_active ? 'deactivate-btn' : 'activate-btn'}
                    onClick={() => toggleUserStatus(user.id, user.is_active)}
                  >
                    {user.is_active ? 'Deactivate' : 'Activate'}
                  </button>
                  <button 
                    className="delete-btn"
                    onClick={() => deleteUser(user.id)}
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default AdminDashboard;