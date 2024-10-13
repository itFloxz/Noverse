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
        'uid64': uid,
        'token': token
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        //API call
        try {
            const response = await axiosInstance.patch('/auth/set-new-password', data);
            const result = response.data;
            if (response.status === 200) {
                navigate('/login');
                toast.success(result.message);
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
                            <label htmlFor="">New Password:</label>
                            <input
                                type="password"
                                className='email-form'
                                name="password"
                                value={newpasswords.password}
                                onChange={handleChange}
                            />
                        </div>
                        <div className='form-group'>
                            <label htmlFor="">Confirm Password:</label>
                            <input
                                type="password"
                                className='email-form'
                                name="confirm_password"
                                value={newpasswords.confirm_password}
                                onChange={handleChange}
                            />
                        </div>
                        <button type='submit' className='vbtn'>Submit</button>
                    </form>
                </div>
            </div>
        </div>
    );
};
