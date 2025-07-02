"use client";

import Link from "next/link";
import { Navbar, NavBody, NavItems, MobileNav, MobileNavHeader, MobileNavToggle, MobileNavMenu, NavbarLogo, NavbarButton } from "./resizable-navbar";
import { Moon, Sun } from "lucide-react";
import { useState } from "react";

export function LandingNavbar({
  dark,
  onToggleDark,
}: {
  dark: boolean;
  onToggleDark(): void;
}) {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const navItems = [
    { name: "Features", link: "#features" },
    { name: "How It Works", link: "#how-it-works" },
    { name: "Testimonials", link: "#testimonials" },
    { name: "Pricing", link: "#pricing" },
  ];

  return (
    <Navbar>
      {/* Desktop */}
      <NavBody>
        <NavbarLogo />

        <NavItems items={navItems} />

        <div className="flex items-center gap-4">
          <button
            onClick={onToggleDark}
            aria-label="Toggle dark mode"
            className="text-xl"
          >
            {dark ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
          </button>

          <NavbarButton as={Link} href="/auth/login" variant="secondary">
            Login
          </NavbarButton>
          <NavbarButton as={Link} href="/auth/register" variant="primary">
            Sign Up
          </NavbarButton>
        </div>
      </NavBody>

      {/* Mobile */}
      <MobileNav>
        <MobileNavHeader>
          <NavbarLogo />
          <MobileNavToggle
            isOpen={isMobileMenuOpen}
            onClick={() => setIsMobileMenuOpen((o) => !o)}
          />
        </MobileNavHeader>

        <MobileNavMenu
          isOpen={isMobileMenuOpen}
          onClose={() => setIsMobileMenuOpen(false)}
        >
          {navItems.map((item, idx) => (
            <a
              key={idx}
              href={item.link}
              onClick={() => setIsMobileMenuOpen(false)}
              className="block px-2 py-1 text-neutral-600 dark:text-neutral-300"
            >
              {item.name}
            </a>
          ))}

          <button
            onClick={() => {
              onToggleDark();
              setIsMobileMenuOpen(false);
            }}
            className="text-xl px-2 py-1"
          >
            {dark ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
          </button>

          <div className="flex flex-col gap-4 pt-4">
            <NavbarButton
              variant="secondary"
              className="w-full"
              onClick={() => setIsMobileMenuOpen(false)}
            >
              Login
            </NavbarButton>
            <NavbarButton
              variant="primary"
              className="w-full"
              onClick={() => setIsMobileMenuOpen(false)}
            >
              Sign Up
            </NavbarButton>
          </div>
        </MobileNavMenu>
      </MobileNav>
    </Navbar>
  );
}
