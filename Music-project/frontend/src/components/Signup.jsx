import React from "react";

const Signup = () => {
  return (
    <div>
      <div className="form-container">
        <div style={{ width: "100%" }} className="wrapper">
          <h2>Create Account</h2>
          <form>
            <div className="form-group">
              <label htmlFor="">Email Address:</label>
              <input type="text" className="email-form" name="email" />
            </div>
            <div className="form-group">
              <label htmlFor="">First Name:</label>
              <input type="text" className="email-form" name="First_name" />
            </div>
            <div className="form-group">
              <label htmlFor="">Last Name:</label>
              <input type="text" className="email-form" name="Last_name" />
            </div>
            <div className="form-group">
              <label htmlFor="">Password:</label>
              <input type="password" className="email-form" name="password" />
            </div>
            <div className="form-group">
              <label htmlFor="">Confirm Password:</label>
              <input
                type="password"
                className="email-form"
                name="confirm_password"
              />
            </div>
            <input type="submit" value="Submit" className="submitButton" />
          </form>
        </div>
      </div>
    </div>
  );
};

export default Signup;
