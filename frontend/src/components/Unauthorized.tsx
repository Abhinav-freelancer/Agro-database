import React from 'react';
import { Link } from 'react-router-dom';
import './Unauthorized.css';

const Unauthorized: React.FC = () => {
  return (
    <div className="unauthorized-container">
      <h1>Unauthorized Access</h1>
      <p>
        You do not have permission to access this resource. 
        Please contact an administrator if you believe this is an error.
      </p>
      <Link to="/">Return to Dashboard</Link>
    </div>
  );
};

export default Unauthorized;