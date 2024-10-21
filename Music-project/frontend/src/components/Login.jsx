import axios from "axios";
import React, { useState ,useEffect} from "react";
import { toast } from "react-toastify";
import { useNavigate,Link } from "react-router-dom";

import Header from "./Header"


const Login = () => {
  const navigate=useNavigate()
  const [logindata, setLoginData]=useState({
    email:"",
    password:"",
  })
  const [error, setError]=useState("")
  const [isLoading, setIsLoading]=useState(false)

  useEffect(() => {
    const token = localStorage.getItem('access');
    if (token) {
      navigate('/dashboard'); // เปลี่ยนไปหน้า dashboard ถ้ามี token
    }
  }, [navigate]); // เพิ่ม dependency เพื่อให้ navigate ทำงานอย่างถูกต้อง



  const handleOnChange = (e)=> {
    setLoginData({...logindata, [e.target.name]:e.target.value})
  }

  const handleSubmit = async (e)=>{
    e.preventDefault()
    const {email, password}=logindata
    if (!email || !password) {
      setError("emaill and password are required")
    }else{
      setIsLoading(true)
      const res = await axios.post("http://localhost:8000/api/v1/auth/login/", logindata)
      const response=res.data
      console.log(response)
      setIsLoading(false)
      const user={
        "email":response.email,
        "names":response.full_name
      }
      if(res.status === 200) {
        localStorage.setItem("user", JSON.stringify(user))
        localStorage.setItem('access', JSON.stringify(response.access_token))
        localStorage.setItem('refresh', JSON.stringify(response.refresh_token))
        navigate("/dashboard")
        toast.success("login Successfull")
      }
    }
  }
  return (
    <div>
    {/* <Header></Header>   */}
      <div className="form-container">
        <div style={{ width: "100%" }} className="wrapper">
          <form onSubmit={handleSubmit}>
            {isLoading && (
              <p>Loading....</p>
            )}
            <h2>Login</h2>
            <div className="form-group">
              <label htmlFor="">Email Address:</label>
              <input type="text" className="email-form" name="email" value={logindata.email} onChange={handleOnChange}/>
            </div>

            <div className="form-group">
              <label htmlFor="">Password:</label>
              <input type="password" className="email-form" name="password" value={logindata.password} onChange={handleOnChange}/>
            </div>

            <input type="submit" value="Login" className="submitButton" />
            <p><a href="/signup">Register</a></p>
            <p className='pass-link'><Link to={'/forget_password'}>forgot password</Link></p>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Login;
