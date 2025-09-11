export default function Avatar({ username }) {
  return (
    <div className="h-8 w-8 flex items-center justify-center rounded-full bg-primary text-primary-foreground font-semibold cursor-pointer hover:bg-primary/90 transition-colors select-none">
      {username.charAt(0).toUpperCase()}
    </div>
  );
}