import { LayoutDashboard, CheckSquare } from "lucide-react";
import { MessageSquare } from "lucide-react";
import { NavLink } from "react-router-dom";

const Sidebar = () => {
    const menuItems = [
        {
            path: "/dashboard",
            label: "Dashboard",
            icon: LayoutDashboard,
        },
        {
            path: "/",
            label: "Tasks",
            icon: CheckSquare,
        },
        {
            path: "/chat",
            label: "Chat",
            icon: MessageSquare,
        },
    ];

    return (
        <div className="w-64 bg-card border-r border-sidebar-border h-screen">
            <div className="p-6">
                <div className="text-sm text-muted-foreground mb-6">Menu</div>
                <nav className="space-y-2">
                    {menuItems.map((item) => {
                        const Icon = item.icon;
                        return (
                            <NavLink
                                key={item.path}
                                to={item.path}
                                className={({ isActive }) =>
                                    `w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left transition-all duration-200 ${
                                        isActive
                                            ? "bg-primary text-primary-foreground shadow-sm"
                                            : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                                    }`
                                }
                            >
                                <Icon size={18} />
                                {item.label}
                            </NavLink>
                        );
                    })}
                </nav>
            </div>
        </div>
    );
};

export default Sidebar;
