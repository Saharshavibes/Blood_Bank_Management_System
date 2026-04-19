import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import axios from "axios";

import { Button } from "@/components/ui/Button";
import { TextField } from "@/components/ui/TextField";
import { useAuth } from "@/context/AuthContext";

export function RegisterHospitalPage() {
  const navigate = useNavigate();
  const { registerHospital } = useAuth();

  const [form, setForm] = useState({
    email: "",
    password: "",
    name: "",
    address: "",
    city: "",
    latitude: "",
    longitude: "",
    contact_phone: "",
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onChange = (key: keyof typeof form, value: string) => {
    setForm((prev) => ({ ...prev, [key]: value }));
  };

  const onSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      await registerHospital({
        email: form.email,
        password: form.password,
        name: form.name,
        address: form.address,
        city: form.city,
        latitude: form.latitude ? Number(form.latitude) : undefined,
        longitude: form.longitude ? Number(form.longitude) : undefined,
        contact_phone: form.contact_phone,
      });
      navigate("/auth/login", { replace: true });
    } catch (submitError) {
      if (axios.isAxiosError(submitError)) {
        setError(submitError.response?.data?.detail ?? "Registration failed.");
      } else {
        setError("Registration failed.");
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center p-4">
      <form className="glass-card w-full max-w-xl space-y-4 p-6" onSubmit={onSubmit}>
        <div>
          <p className="text-xs font-mono uppercase tracking-[0.2em] text-black/50">Hospital Portal Setup</p>
          <h1 className="mt-2 text-2xl font-extrabold">Register Hospital Access</h1>
        </div>

        <div className="grid gap-3 sm:grid-cols-2">
          <TextField label="Hospital name" value={form.name} onChange={(e) => onChange("name", e.target.value)} required />
          <TextField label="City" value={form.city} onChange={(e) => onChange("city", e.target.value)} required />
          <TextField label="Portal email" type="email" value={form.email} onChange={(e) => onChange("email", e.target.value)} required />
          <TextField label="Password" type="password" value={form.password} onChange={(e) => onChange("password", e.target.value)} required />
          <TextField label="Contact phone" value={form.contact_phone} onChange={(e) => onChange("contact_phone", e.target.value)} required />
          <TextField label="Address" value={form.address} onChange={(e) => onChange("address", e.target.value)} required />
          <TextField label="Latitude" value={form.latitude} onChange={(e) => onChange("latitude", e.target.value)} />
          <TextField label="Longitude" value={form.longitude} onChange={(e) => onChange("longitude", e.target.value)} />
        </div>

        {error ? <p className="text-sm text-rose-600">{error}</p> : null}

        <Button type="submit" fullWidth disabled={isSubmitting}>
          {isSubmitting ? "Registering..." : "Create hospital account"}
        </Button>

        <p className="text-sm text-black/65">
          Already registered? <Link className="font-semibold text-calm" to="/auth/login">Sign in</Link>
        </p>
      </form>
    </div>
  );
}
