import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import axios from "axios";

import { Button } from "@/components/ui/Button";
import { TextField } from "@/components/ui/TextField";
import { useAuth } from "@/context/AuthContext";
import { BLOOD_TYPES, type BloodType } from "@/types/domain";

type DonorRegistrationForm = {
  email: string;
  password: string;
  full_name: string;
  phone: string;
  date_of_birth: string;
  blood_type: BloodType;
  medical_history: string;
};

export function RegisterDonorPage() {
  const navigate = useNavigate();
  const { registerDonor } = useAuth();

  const [form, setForm] = useState<DonorRegistrationForm>({
    email: "",
    password: "",
    full_name: "",
    phone: "",
    date_of_birth: "",
    blood_type: "O+",
    medical_history: "",
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onChange = <K extends keyof DonorRegistrationForm>(key: K, value: DonorRegistrationForm[K]) => {
    setForm((prev) => ({ ...prev, [key]: value }));
  };

  const onSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      await registerDonor({
        ...form,
        medical_history: form.medical_history || undefined,
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
          <p className="text-xs font-mono uppercase tracking-[0.2em] text-black/50">Donor Registration</p>
          <h1 className="mt-2 text-2xl font-extrabold">Join the Donor Network</h1>
        </div>

        <div className="grid gap-3 sm:grid-cols-2">
          <TextField label="Full name" value={form.full_name} onChange={(e) => onChange("full_name", e.target.value)} required />
          <TextField label="Phone" value={form.phone} onChange={(e) => onChange("phone", e.target.value)} required />
          <TextField label="Email" type="email" value={form.email} onChange={(e) => onChange("email", e.target.value)} required />
          <TextField label="Password" type="password" value={form.password} onChange={(e) => onChange("password", e.target.value)} required />
          <TextField
            label="Date of birth"
            type="date"
            value={form.date_of_birth}
            onChange={(e) => onChange("date_of_birth", e.target.value)}
            required
          />
          <label className="block space-y-1.5">
            <span className="text-sm font-medium text-black/80">Blood group</span>
            <select
              className="w-full rounded-xl border border-black/15 bg-white px-3 py-2.5 text-sm"
              value={form.blood_type}
              onChange={(e) => onChange("blood_type", e.target.value as BloodType)}
            >
              {BLOOD_TYPES.map((type) => (
                <option key={type} value={type}>
                  {type}
                </option>
              ))}
            </select>
          </label>
        </div>

        <label className="block space-y-1.5">
          <span className="text-sm font-medium text-black/80">Medical history (optional)</span>
          <textarea
            className="min-h-24 w-full rounded-xl border border-black/15 bg-white px-3 py-2.5 text-sm"
            value={form.medical_history}
            onChange={(e) => onChange("medical_history", e.target.value)}
          />
        </label>

        {error ? <p className="text-sm text-rose-600">{error}</p> : null}

        <Button type="submit" fullWidth disabled={isSubmitting}>
          {isSubmitting ? "Registering..." : "Create donor account"}
        </Button>

        <p className="text-sm text-black/65">
          Already registered? <Link className="font-semibold text-calm" to="/auth/login">Sign in</Link>
        </p>
      </form>
    </div>
  );
}
