import { Form, useNavigation } from "react-router-dom";
import Input from "./ui/Input";
import Button from "./ui/Button";

export default function AuthForm() {
    const navigation = useNavigation();
    const isSubmitting = navigation.state === 'submitting';
    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary/10 to-secondary/10 p-4">
            <div className="bg-white border rounded-lg shadow w-full max-w-md">
                <div className="p-6 border-b text-center">
                    <div className="mb-4">
                        <h1 className="text-3xl font-bold text-primary mb-2">TimelyAI</h1>
                    </div>
                    <h2 className="text-xl font-semibold mb-1">Login</h2>
                </div>
                <div className="p-6">
                    <Form method="post" className="space-y-4">
                        <div className="space-y-2">
                            <Input htmlFor="accountid" label="Account Id" id="accountid" name="accountid"
                                type="text"
                                placeholder="Enter your account id"
                                required />
                        </div>
                        <div className="space-y-2">
                            <Input htmlFor="username" label="Username" id="username" name="username"
                                type="text"
                                placeholder="Enter your username"
                                required />
                        </div>
                        <div className="space-y-2">
                            <Input htmlFor="password" label="Password" id="password" name="password"
                                type="password"
                                placeholder="Enter your password"
                                required />
                        </div>
                        <Button variant="default" className="w-full" disabled={isSubmitting}>
                            {isSubmitting ? "Signing in..." : "Sign In"}
                        </Button>
                    </Form>
                </div>
            </div>
        </div>
    )
}
