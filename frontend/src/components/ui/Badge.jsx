export default function Badge({ children, status, ...props}) {

    const getStatusColor = (status) => {
        switch (status) {
            case "completed":
                return "bg-green-100 text-green-700";
            case "in-progress":
                return "bg-blue-100 text-blue-700";
            case "paused":
                return "bg-yellow-100 text-yellow-700";
            default:
                return "bg-gray-100 text-gray-700";
        }
    };

    const classes = getStatusColor(status);

    return (
        <span className={`inline-block rounded px-2 py-0.5 font-semibold text-xs ${classes}`} {...props}>
            {children}
        </span>
    );
}