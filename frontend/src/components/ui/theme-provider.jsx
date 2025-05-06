import { createContext, useContext, useEffect, useState } from "react";

// Create context for theme management
const ThemeContext = createContext({
  theme: "dark",
  setTheme: () => null,
  toggleTheme: () => null,
});

export const ThemeProvider = ({
  children,
  defaultTheme = "dark",
  storageKey = "vite-ui-theme",
}) => {
  const [theme, setTheme] = useState(
    () => localStorage.getItem(storageKey) || defaultTheme
  );

  useEffect(() => {
    // Apply theme class to document element
    const root = window.document.documentElement;
    root.classList.remove("light", "dark");
    root.classList.add(theme);
    localStorage.setItem(storageKey, theme);
  }, [theme, storageKey]);

  const toggleTheme = () => {
    setTheme(theme === "dark" ? "light" : "dark");
  };

  const value = {
    theme,
    setTheme,
    toggleTheme,
  };

  return (
    <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>
  );
};

// Hook to access theme context
export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (context === undefined)
    throw new Error("useTheme must be used within a ThemeProvider");
  return context;
};
