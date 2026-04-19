import { useState, type FormEvent } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import axios from "axios";

import { Button } from "@/components/ui/Button";
import { TextField } from "@/components/ui/TextField";
import { useAuth } from "@/context/AuthContext";
import { roleHomePath } from "@/lib/roleHome";

export function LoginPage() {
  const navigate = useNavigate();
  const { login, isAuthenticated, user } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (isAuthenticated && user) {
    return <Navigate to={roleHomePath[user.role]} replace />;
  }

  const onSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      await login({ email, password });
      navigate("/", { replace: true });
    } catch (submitError) {
      if (axios.isAxiosError(submitError)) {
        setError(submitError.response?.data?.detail ?? "Login failed.");
      } else {
        setError("Login failed.");
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center p-4">
      <form className="glass-card w-full max-w-md space-y-4 p-6" onSubmit={onSubmit}>
        <div>
          <p className="text-xs font-mono uppercase tracking-[0.2em] text-black/50">Secure Access</p>
          <h1 className="mt-2 text-2xl font-extrabold">Sign in to BBMS</h1>
          <p className="mt-1 text-sm text-black/60">Use your donor, admin, or hospital credentials.</p>
        </div>

        <TextField
          label="Email"
          type="email"
          autoComplete="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          required
        />

        <TextField
          label="Password"
          type="password"
          autoComplete="current-password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          required
        />

        {error ? <p className="text-sm text-rose-600">{error}</p> : null}

        <Button type="submit" fullWidth disabled={isSubmitting}>
          {isSubmitting ? "Signing in..." : "Sign in"}
        </Button>

        <p className="text-sm text-black/65">
          New donor? <Link className="font-semibold text-calm" to="/auth/register-donor">Create account</Link>
        </p>
        <p className="text-sm text-black/65">
          New hospital? <Link className="font-semibold text-calm" to="/auth/register-hospital">Register portal</Link>
        </p>
      </form>
    </div>
  );
}
