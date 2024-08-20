import React, { useState } from "react";
import { Navigate, useNavigate, useParams } from "react-router-dom"
import axiosInstance from "../utlils/axiosInstance";
import { toast } from "react-toastify";

const ResetPassword = () => {
  const navigate=useNavigate()
  const {uid, token}=useParams()
  const [newpassword, setNewPassword]=useState({
    password:'',
    confirm_password:''
  })
  const handleChange=(e)=> {
    setNewPassword({...newpassword, [e.target.name]:e.target.value})
  }
  const data={
    'password':newpassword.password,
    'confirm_password':newpassword.confirm_password,
    'uidb64':uid,
    'token':token
  }

  const handleSubmit = async (e)=>{
    e.preventDefault()
    //make api call
    const response = await axiosInstance.patch('/auth/set-new-password/', data)
    const result = response.data
    if(response.status === 200) {
      navigate('/login')
      toast.success(result.message)
    }
  }
  
  return (
    <div>
      <div className='form-container'>
        <div className="wrapper" style={{width:"100%"}}>
          <h2>Enter your New password</h2>
          <form action="" onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="">New Password</label>
              <input type="text" 
              className="email-form"
              name="password"
              value={newpassword.password}
              onChange={handleChange}
              />
            </div>
            <div className="form-group">
              <label htmlFor="">Confirm Password</label>
              <input type="text" 
              className="email-form" 
              name="confirm_password" 
              value={newpassword.confirm_password}
              onChange={handleChange}/>
            </div>
            <button type="submit" className="vbtn">Submit</button>
          </form>
        </div>
      </div>
    </div>
  )
}

export default ResetPassword