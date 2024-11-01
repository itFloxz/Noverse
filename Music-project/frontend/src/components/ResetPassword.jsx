import React, { useState } from 'react';
import { useNavigate, useParams } from "react-router-dom";
import axiosInstance from '../utlils/axiosInstance';
import { toast } from 'react-toastify';
import Stars from './star';

export const ResetPassword = () => {
    const navigate = useNavigate();
    const { uid, token } = useParams();
    const [newpasswords, setNewPasswords] = useState({
        password: '',
        confirm_password: ''
    });

    const [passwordConditions, setPasswordConditions] = useState({
        length: false,
        uppercase: false,
        lowercase: false,
        number: false,
        specialChar: false,
    });
    const [showTooltip, setShowTooltip] = useState(false);

    const validatePassword = (password) => {
        const conditions = {
            length: password.length >= 8,
            uppercase: /[A-Z]/.test(password),
            lowercase: /[a-z]/.test(password),
            number: /[0-9]/.test(password),
            specialChar: /[!@#$%^&*(),.?":{}|<>]/.test(password),
        };
        setPasswordConditions(conditions);
    };

    const handleChange = (e) => {
        const { name, value } = e.target;
        setNewPasswords({ ...newpasswords, [name]: value });
        if (name === "password") validatePassword(value);
    };

    const data = {
        password: newpasswords.password,
        confirm_password: newpasswords.confirm_password,
        uidb64: uid,
        token: token
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
        <div style={styles.container}>
            <div style={styles.wrapper}>
            <Stars />
                <h2>Enter your New Password</h2>
                <form onSubmit={handleSubmit} style={styles.form}>
                    <div style={{ ...styles.formGroup, position: 'relative' }}>
                        <label>New Password:</label>
                        <input
                            type="password"
                            name="password"
                            value={newpasswords.password}
                            onChange={handleChange}
                            style={styles.input}
                            onFocus={() => setShowTooltip(true)}
                            onBlur={() => setShowTooltip(false)}
                        />
                        {showTooltip && (
                            <div style={styles.tooltip}>
                                <p>Password must:</p>
                                <ul>
                                    <li style={passwordConditions.length ? styles.valid : styles.invalid}>
                                        Be at least 8 characters long
                                    </li>
                                    <li style={passwordConditions.uppercase ? styles.valid : styles.invalid}>
                                        Contain at least one uppercase letter
                                    </li>
                                    <li style={passwordConditions.lowercase ? styles.valid : styles.invalid}>
                                        Contain at least one lowercase letter
                                    </li>
                                    <li style={passwordConditions.number ? styles.valid : styles.invalid}>
                                        Contain at least one number
                                    </li>
                                    <li style={passwordConditions.specialChar ? styles.valid : styles.invalid}>
                                        Contain at least one special character (e.g., @, #, $)
                                    </li>
                                </ul>
                            </div>
                        )}
                    </div>

                    <div style={styles.formGroup}>
                        <label>Confirm Password:</label>
                        <input
                            type="password"
                            name="confirm_password"
                            value={newpasswords.confirm_password}
                            onChange={handleChange}
                            style={styles.input}
                        />
                    </div>

                    <button type='submit' style={styles.button}>Submit</button>
                </form>
            </div>
        </div>
    );
};

const styles = {
    container: {
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '60vh',
        borderRadius: '20px',
        backgroundColor: 'rgba(255, 255, 255, 0.5)',
    },
    wrapper: {
        width: '800px',
        padding: '30px',
        borderRadius: '8px',
        boxShadow: '0 4px 8px rgba(0, 0, 0, 0.1)',
        backgroundColor: '#fff',
        textAlign: 'center',
    },
    form: {
        display: 'flex',
        flexDirection: 'column',
    },
    formGroup: {
        marginBottom: '15px',
        textAlign: 'left',
    },
    input: {
        width: '100%',
        padding: '10px',
        marginTop: '5px',
        borderRadius: '4px',
        border: '1px solid #ddd',
        fontSize: '16px',
    },
    button: {
        marginTop: '15px',
        padding: '10px 20px',
        backgroundColor: '#1E2A47',
        color: '#fff',
        border: 'none',
        borderRadius: '4px',
        fontSize: '16px',
        cursor: 'pointer',
        transition: 'background-color 0.3s',
    },
    tooltip: {
        position: 'absolute',
        top: '0',
        right: '-300px',
        width: '250px',
        backgroundColor: '#fff',
        border: '1px solid #ddd',
        borderRadius: '8px',
        padding: '10px',
        boxShadow: '0 4px 8px rgba(0, 0, 0, 0.1)',
        textAlign: 'left',
        zIndex: 1,
    },
    valid: {
        color: 'green',
    },
    invalid: {
        color: 'red',
    },
};

export default ResetPassword;
