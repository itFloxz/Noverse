import React, { useState } from "react";
import axios from "axios"
import { useNavigate } from "react-router-dom"
import { toast } from "react-toastify"
import Header from "./Header"

const Signup = () => {
  const navigate = useNavigate()
  const [formdata,setFormData]=useState({
    email:"",
    first_name:"",
    last_name:"",
    password:"",
    password2:""
  })

  const [error, setError]=useState("")

  const handleOnChange = (e)=>{
    setFormData({...formdata,[e.target.name]:e.target.value})
  }
const {email, first_name, last_name, password, password2}=formdata
  
const handleSubmit = async (e)=>{
    e.preventDefault()
    if(!email || !first_name || !last_name || !password || !password2){
      setError("all fields are required")
    }else {
      console.log(formdata)
      //make call to api
      const res = await axios.post("http://localhost:8000/api/v1/auth/register/", formdata)
      //check our response
      const response = res.data
      console.log(response)
      if (res.status === 201){
      //redurect to verifyemail component
        navigate("/otp/verify")
        toast.success(response.massage)

      }
      
      //server error pass to error
    }
    
  }


  return (
    <div>
      <Header></Header>
      <div className="form-container">
        <div style={{ width: "100%" }} className="wrapper">
          <h2>Create Account</h2>
          
          <form onSubmit={handleSubmit}>
          <p style={{color:"red", padding:"1px"}}>{error ? error : ""}</p>
            <div className="form-group">
              <label htmlFor="">Email Address:</label>
              <input 
              type="text" className="email-form" name="email" value={email} onChange={handleOnChange}/>
            </div>
            <div className="form-group">
              <label htmlFor="">First Name:</label>
              <input type="text" className="email-form" name="first_name" value={first_name} onChange={handleOnChange}/>
            </div>
            <div className="form-group">
              <label htmlFor="">Last Name:</label>
              <input type="text" className="email-form" name="last_name" value={last_name } onChange={handleOnChange}/>
            </div>
            <div className="form-group">
              <label htmlFor="">Password:</label>
              <input type="password" className="email-form" name="password" value={password} onChange={handleOnChange}/>
            </div>
            <div className="form-group">
              <label htmlFor="">Confirm Password:</label>
              <input
                type="password" className="email-form" name="password2" value={password2} onChange={handleOnChange}/>
            </div>
            <input type="submit" value="Submit" className="submitButton" />
          </form>
        </div>
      </div>
    </div>
  );
};

export default Signup;
