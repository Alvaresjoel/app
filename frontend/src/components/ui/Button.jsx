const BUTTON_VARIANTS = {
    default: "bg-primary text-white hover:bg-primary/90",
    ghost: "bg-transparent hover:bg-gray-200",
    destructive: "bg-red-500 text-white hover:bg-red-600",
};

export default function Button({ children, className = "", variant = "default", ...props }) {
    return (
        <button
            className={`rounded px-3 py-2 text-sm transition-colors ${BUTTON_VARIANTS[variant]} ${className}`}
            {...props}
        >
            {children}
        </button>
    );
}