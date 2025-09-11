import AuthForm from "../components/AuthForm";
import { login } from "../services/api";
import { useContext, useEffect } from "react";
import { UserContext } from "../store/user-context";
import { useActionData, useNavigate } from "react-router-dom";
import {toast} from "react-toastify"

export default function Login() {
    const navigate = useNavigate();
    const { onLogin } = useContext(UserContext);
    const userData = useActionData();

    useEffect(() => {
        if (userData?.success) {
            onLogin(userData.data); // Pass only the `data` part
            toast.success(userData?.message || "Login successful");
            console.log(userData)
            navigate("/");
        }
        if (userData?.success === false){
            toast.error(userData?.message || "Login failed");
        }
    }, [userData]);

    return (
        <AuthForm errorMessage={!userData?.success ? userData?.message : null} />
    );
}

export async function action({ request }) {
    const formData = await request.formData();
    const accountid = formData.get("accountid");
    const username = formData.get("username");
    const password = formData.get("password");

    const response = await login({ accountid, username, password });

    return response;
}
