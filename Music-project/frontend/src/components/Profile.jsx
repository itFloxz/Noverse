import Reac, {useEffect} from "react";
import { useNavigate } from "react-router-dom"

const Profile = () => {
  const navigate=useNavigate()
  const user = JSON.parse(localStorage.getItem('user'))
  const jwt_access=localStorage.getItem('access')

  useEffect(()=> {
    if (jwt_access === null && !user ){
      navigate("/login")
    }
  },[])

  return (
  <div>
    <h2>hi {user && user.full_name}</h2>
    <p style={{textAlign:"center"}}>welcome to your profile</p>
    <button className="logout-btn">Logout</button>

  </div>
  )
};

export default Profile;
