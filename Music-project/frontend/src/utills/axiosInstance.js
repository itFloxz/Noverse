import axios from "axios";
import { jwtDecode } from "jwt-decode"
import dayjs from "dayjs"


const token = localStorage.getItem('access') ? JSON.parse(localStorage.getItem('access')) : ""
const refresh_token = localStorage.getItem('refresh') ? JSON.parse(localStorage.getItem('refresh')) : ""

const baseUrl= "http://localhost:8000/api/v1"
const axiosInstance = axios.create({
    baseURL:baseUrl,
    'Content-type' : 'application/json',
    headers:{ 'Authorization' : localStorage.getItem('access') ?  `Bearer ${token}` : null}
})

 axiosInstance.interceptors.request.use( async req => {
    if (token) {
        req.headers['Authorization'] = `Bearer ${token}`
        const user = jwtDecode(token)
        const isExpired=dayjs.unix(user.exp).diff(dayjs()) < 1 
        console.log(isExpired)

        return req
    }
 })

console.log("axioInstance : ")


export default axiosInstance