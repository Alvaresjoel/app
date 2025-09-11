import Sidebar from "../components/Sidebar.jsx";
import Navbar from "../components/Navbar";
import { Outlet, Navigate } from "react-router-dom";
import { TasksContextProvider } from "../store/tasks-context";

export default function RootPage() {
    return (
        <div className="grid grid-rows-[auto,1fr] h-screen">
            <Navbar />

            <div className="grid grid-cols-[260px,1fr] min-h-0 overflow-hidden">
                <Sidebar />

                <TasksContextProvider>
                    <div className="overflow-y-auto">
                        <Outlet />
                    </div>
                </TasksContextProvider>
            </div>
        </div>
    )
}