import { redirect } from "react-router-dom";

export function getToken(){
    try {
        const token = localStorage.getItem('token') || sessionStorage.getItem('token');
        return token || null;
    } catch (e) {
        return null;
    }
}


export function chechAuth(){
    const token = getToken();
    if (!token){
        return redirect("/login");
    }
    return null;
}