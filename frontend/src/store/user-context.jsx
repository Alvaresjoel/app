import { createContext, useEffect, useState } from 'react';

const DOMAIN = 'http://localhost:3000/';

export const UserContext = createContext({
    user: null,
    onLogin: () => { },
    onLogout: () => { },
});

export function UserContextProvider({ children }) {
    const [user, setUser] = useState({
        "message": "",
        "username": "",
        "guid": "",
        "role": "",
        "user_id": null,
        "ace_user_id": "",
        "account_id": ""
    });

    useEffect(() => {
        try {
            const storedUser = localStorage.getItem('user');
            if (storedUser) {
                setUser(prev => ({ ...prev, ...JSON.parse(storedUser) }));
            }
        } catch (_) { /* ignore */ }
    }, []);

    function onLogin(userData) {
        localStorage.setItem('token', userData.access_token)
        localStorage.setItem('refresh-token', userData.refresh_token)
        localStorage.setItem('user', JSON.stringify(userData))
        setUser(prev => ({...prev, ...userData}));
    }
    function onLogout() {
        setUser(null);
        localStorage.removeItem('token');
        localStorage.removeItem('refresh-token');
        localStorage.removeItem('user');
    }


    const contextValue = {
        user: user,
        onLogin,
        onLogout
    };

    return <UserContext.Provider key={contextValue} value={contextValue}>{children}</UserContext.Provider>;
}