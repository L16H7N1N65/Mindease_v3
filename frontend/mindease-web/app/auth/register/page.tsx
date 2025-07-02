"use client";

import Link from "next/link";
import { signIn } from "next-auth/react";
import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Navbar } from "@/components/Navbar";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

export default function RegisterPage() {
  const router = useRouter();

  const [email, setEmail] = useState("");
  const [emailError, setEmailError] = useState("");
  const [password, setPassword] = useState("");
  const [passwordError, setPasswordError] = useState("");
  const [confirm, setConfirm] = useState("");
  const [confirmError, setConfirmError] = useState("");
  const [terms, setTerms] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  // ---- validations ----
  useEffect(() => {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    setEmailError(email && !re.test(email) ? "Invalid email" : "");
  }, [email]);

  useEffect(() => {
    const re = /^(?=.*\d)(?=.*[!@#$%^&*]).{8,}$/;
    setPasswordError(
      password && !re.test(password)
        ? "Min 8 chars, include number & special"
        : ""
    );
  }, [password]);

  useEffect(() => {
    setConfirmError(confirm && confirm !== password ? "Doesn’t match" : "");
  }, [confirm, password]);

  const canSubmit =
    !!email &&
    !emailError &&
    !!password &&
    !passwordError &&
    !!confirm &&
    !confirmError &&
    terms;

  // ---- submit handler ----
  const handleCreateAccount = async () => {
    if (!canSubmit) return;
    setSubmitError(null);
    setLoading(true);

    try {
      const res = await fetch("/api/v1/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      if (!res.ok) {
        const payload = await res.json();
        throw new Error(payload.detail || "Registration failed");
      }

      const { access_token } = await res.json();
      localStorage.setItem("mindease_token", access_token);
      router.push("/dashboard");
    } catch (err: unknown) {
      // narrow error
      const message =
        err instanceof Error ? err.message : "Registration failed";
      setSubmitError(message);
    } finally {
      setLoading(false);
    }
  };

  // ---- single return ----
  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-primary/10 to-accent/10">
      <Navbar
        logo={
          <div className="flex items-center gap-2">
            <svg viewBox="0 0 24 24" className="h-8 w-8 text-primary">
              <path
                d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z"
                stroke="currentColor"
                strokeWidth="2"
              />
              <path d="M9 15h6M9 9h6" stroke="currentColor" strokeWidth="2" />
            </svg>
            <span className="font-bold text-xl">MindEase</span>
          </div>
        }
      >
        <Button asChild variant="ghost">
          <Link href="/">Home</Link>
        </Button>
      </Navbar>

      <main className="flex-1 flex items-center justify-center px-4 sm:px-6 lg:px-8 py-16">
        <div className="w-full max-w-md space-y-6">
          <div className="text-center">
            <h1 className="text-4xl font-extrabold text-primary">
              Join MindEase
            </h1>
            <p className="mt-2 text-sm text-muted-foreground">
              Create your account & start your journey
            </p>
          </div>

          <Card className="shadow-xl">
            <CardHeader>
              <CardTitle>Create Account</CardTitle>
              <CardDescription>Fill in the fields below</CardDescription>
            </CardHeader>

            <CardContent className="space-y-4">
              {submitError && (
                <p className="text-sm text-red-600">{submitError}</p>
              )}

              <div>
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="you@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className={
                    emailError ? "border-red-500 focus:ring-red-500" : ""
                  }
                />
                {emailError && (
                  <p className="text-xs text-red-600 mt-1">{emailError}</p>
                )}
              </div>

              <div>
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className={
                    passwordError ? "border-red-500 focus:ring-red-500" : ""
                  }
                />
                {passwordError && (
                  <p className="text-xs text-red-600 mt-1">{passwordError}</p>
                )}
              </div>

              <div>
                <Label htmlFor="confirm">Confirm Password</Label>
                <Input
                  id="confirm"
                  type="password"
                  value={confirm}
                  onChange={(e) => setConfirm(e.target.value)}
                  className={
                    confirmError ? "border-red-500 focus:ring-red-500" : ""
                  }
                />
                {confirmError && (
                  <p className="text-xs text-red-600 mt-1">{confirmError}</p>
                )}
              </div>

              <div className="flex items-center space-x-2 pt-2">
                <input
                  id="terms"
                  type="checkbox"
                  className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                  checked={terms}
                  onChange={(e) => setTerms(e.target.checked)}
                />
                <Label htmlFor="terms" className="text-sm">
                  I agree to the{" "}
                  <Link href="/terms" className="text-primary hover:underline">
                    Terms
                  </Link>{" "}
                  and read the{" "}
                  <Link href="/privacy" className="text-primary hover:underline">
                    Privacy Policy
                  </Link>
                </Label>
              </div>
            </CardContent>

            <CardFooter className="flex flex-col space-y-3">
              <Button
                className="w-full"
                disabled={!canSubmit || loading}
                onClick={handleCreateAccount}
              >
                {loading ? "Creating…" : "Create Account"}
              </Button>

              <Button
                variant="outline"
                className="w-full flex items-center justify-center"
                onClick={() => signIn("google")}
              >
                Continue with Google
              </Button>

              <p className="text-xs text-center">
                Already have an account?{" "}
                <Link
                  href="/auth/login"
                  className="font-medium text-primary hover:underline"
                >
                  Login
                </Link>
              </p>
            </CardFooter>
          </Card>
        </div>
      </main>
    </div>
  );
}
