import { useState, useContext } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { Bell, LogOut, X } from "lucide-react";
import Button from "./ui/Button";
import Avatar from "./ui/Avtar";
import Dropdown from "./ui/Dropdown";
import { UserContext } from "../store/user-context"

const NOTIFICATIONS = [
    { id: 1, message: "New task assigned to you", time: "2 min ago" },
    { id: 2, message: "Meeting reminder in 30 minutes", time: "30 min ago" },
    { id: 3, message: "Project deadline approaching", time: "1 hour ago" },
];


export default function Navbar() {
    const [notifications, setNotifications] = useState(NOTIFICATIONS);
    const clearNotifications = () => setNotifications([]);

    const { user, onLogout, isLoading } = useContext(UserContext)
    const navigate = useNavigate();
    const location = useLocation();

    const pathToTitle = {
        "/": "Tasks",
        "/dashboard": "Dashboard",
        "/chat": "Chat",
    };
    const title = pathToTitle[location.pathname] || "Tasks";

    if (!user || user.username === "") {
        return (
            <div className="h-16 bg-white border-b border-gray-200 px-6 flex items-center justify-center shadow-sm">
                <span className="text-gray-600">Loading...</span>
            </div>
        );
    }

    return (
        <div className="h-16 bg-background border-b border-border px-6 flex items-center justify-between">
            <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                    <h1 className="text-2xl font-bold text-primary">TimelyAI</h1>
                    <span className="text-muted-foreground">|</span>
                    <h2 className="text-xl font-semibold text-foreground">{title}</h2>
                </div>
            </div>

            <div className="flex items-center gap-4">
                <Dropdown
                    align="end"
                    trigger={
                        <div className="relative">
                            <Button variant="ghost" className="p-2 rounded-full">
                                <Bell className="h-5 w-5" />
                                {notifications.length > 0 && (
                                    <span className="absolute -top-1 -right-1 h-4 w-4 bg-red-400 text-destructive-foreground text-xs rounded-full flex items-center justify-center">
                                        {notifications.length}
                                    </span>
                                )}
                            </Button>
                        </div>
                    }
                    className="w-80"
                >
                    {({ close }) => (
                        <>
                            <div className="flex items-center justify-between p-2">
                                <span className="font-semibold">Notifications</span>
                                {notifications.length > 0 && (
                                    <Button
                                        variant="ghost"
                                        className="h-6 px-2 text-xs flex items-center"
                                        onClick={() => {
                                            clearNotifications();
                                            close();
                                        }}
                                    >
                                        <X className="h-3 w-3 mr-1" />
                                        Clear
                                    </Button>
                                )}
                            </div>
                            <div className="border-t" />
                            {notifications.length === 0 ? (
                                <div className="p-4 text-center text-muted-foreground text-sm">
                                    No new notifications
                                </div>
                            ) : (
                                notifications.map((notification) => (
                                    <div
                                        key={notification.id}
                                        className="cursor-pointer flex flex-col items-start p-3 hover:bg-gray-50"
                                    >
                                        <span className="text-sm">{notification.message}</span>
                                        <span className="text-xs text-muted-foreground mt-1">
                                            {notification.time}
                                        </span>
                                    </div>
                                ))
                            )}
                        </>
                    )}
                </Dropdown>

                <Dropdown
                    align="end"
                    trigger={<Avatar username={user?.username || "Guest"} />}
                    className="w-56"
                >
                    {({ close }) => (
                        <div>
                            {/* <div
                                className="flex items-center px-4 py-2 cursor-pointer hover:bg-gray-100"
                                onClick={close}
                            >
                                <User className="mr-2 h-4 w-4" />
                                <span>Profile</span>
                            </div>
                            <div
                                className="flex items-center px-4 py-2 cursor-pointer hover:bg-gray-100"
                                onClick={close}
                            >
                                <Settings className="mr-2 h-4 w-4" />
                                <span>Settings</span>
                            </div> */}
                            {/* <div className="border-t my-1" /> */}
                            <div
                                className="flex items-center px-4 py-2 cursor-pointer text-destructive hover:bg-red-50"
                                onClick={() => {
                                    onLogout && onLogout();
                                    navigate('/login');
                                    close();
                                }}
                            >
                                <LogOut className="mr-2 h-4 w-4" />
                                <span>Logout</span>
                            </div>
                        </div>
                    )}
                </Dropdown>
            </div>
        </div>
    );
}