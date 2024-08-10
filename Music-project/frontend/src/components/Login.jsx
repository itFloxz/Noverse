import React, { useState } from "react";

const Login = () => {
  return (
    <div>
      <div className="form-container">
        <div style={{ width: "100%" }} className="wrapper">
          <h2>Login</h2>
          <form>
            <div className="form-group">
              <label htmlFor="">Email Address:</label>
              <input type="text" className="email-form" name="email" />
            </div>

            <div className="form-group">
              <label htmlFor="">Password:</label>
              <input type="password" className="email-form" name="password" />
            </div>

            <input type="submit" value="Login" className="submitButton" />
          </form>
        </div>
      </div>
    </div>
  );
};

export default Login;
