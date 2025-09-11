export default function Card({ children, className = "", ...props }) {
  return (
    <div className={`bg-white border rounded-lg ${className}`} {...props}>
      {children}
    </div>
  );
}