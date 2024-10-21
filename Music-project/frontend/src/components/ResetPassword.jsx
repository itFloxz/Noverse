import React, { useState } from 'react';
import { useNavigate, useParams } from "react-router-dom";
import axiosInstance from '../utlils/axiosInstance';
import { toast } from 'react-toastify';

export const ResetPassword = () => {
    const navigate = useNavigate();
    const { uid, token } = useParams();
    const [newpasswords, setNewPasswords] = useState({
        password: '',
        confirm_password: ''
    });

    const handleChange = (e) => {
        setNewPasswords({ ...newpasswords, [e.target.name]: e.target.value });
    };

    const data = {
        'password': newpasswords.password,
        'confirm_password': newpasswords.confirm_password,
        'uidb64': uid,
        'token': token
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await axiosInstance.patch('/auth/set-new-password/', data);
            if (response.status === 200) {
                navigate('/login');
                toast.success("Password reset successfully!");
            }
        } catch (error) {
            toast.error("An error occurred while resetting the password.");
        }
    };

    return (
        <div>
            <div className='form-container'>
                <div className='wrapper' style={{ width: "100%" }}>
                    <h2>Enter your New Password</h2>
                    <form onSubmit={handleSubmit}>
                        <div className='form-group'>
                            <label>New Password:</label>
                            <input
                                type="password"
                                className='email-form'
                                name="password"
                                value={newpasswords.password}
                                onChange={handleChange}
                            />
                        </div>
                        <div className='form-group'>
                            <label>Confirm Password:</label>
                            <input
                                type="password"
                                className='email-form'
                                name="confirm_password"
                                value={newpasswords.confirm_password}
                                onChange={handleChange}
                            />
                        </div>

                        {/* Password Conditions */}
                        <div className="password-conditions">
                            <p>Password must:</p>
                            <ul>
                                <li>Be at least 8 characters long</li>
                                <li>Contain at least one uppercase letter</li>
                                <li>Contain at least one lowercase letter</li>
                                <li>Contain at least one number</li>
                                <li>Contain at least one special character (e.g., @, #, $)</li>
                            </ul>
                        </div>

                        <button type='submit' className='vbtn'>Submit</button>
                    </form>
                </div>
            </div>
        </div>
    );
};
