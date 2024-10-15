import { useState } from "react";
import { ToastContainer} from 'react-toastify';
import "react-toastify/dist/ReactToastify.css";
import reactLogo from "./assets/react.svg";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import viteLogo from "/vite.svg";
import {Signup, Login, Profile, VerifyEmail, ForgetPassword,FileUploadCrop} from "./components";
import "./App.css";
import { ResetPassword } from "./components/ResetPassword";

function App() {
  const [count, setCount] = useState(0);

  return (
    <>
      <Router>
      <ToastContainer/>
        <Routes>
          <Route path='/' element={<FileUploadCrop />} />
          <Route path='/signup' element={<Signup />} />
          <Route path='/login' element={<Login />} />
          <Route path='/dashboard' element={<Profile />} />
          <Route path='/otp/verify' element={<VerifyEmail />} />
          <Route path='/forget_password' element={<ForgetPassword />} />
          <Route path='/password-reset-confirm/:uid/:token' element={<ResetPassword />}/>
          <Route path='/FileUploadCrop' element={<FileUploadCrop />}/>
        </Routes>
      </Router>
    </>
  );
}

export default App;
