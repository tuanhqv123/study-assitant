import { useEffect, useState } from "react";
import { supabase } from "../lib/supabase";
import { Navigate } from "react-router-dom";

const ProtectedRoute = ({ children }) => {
  const [loading, setLoading] = useState(true);
  const [authenticated, setAuthenticated] = useState(false);

  useEffect(() => {
    const checkAuth = async () => {
      const {
        data: { user },
      } = await supabase.auth.getUser();
      setAuthenticated(!!user);
      setLoading(false);
    };
    checkAuth();
  }, []);

  if (loading) {
    return null; // or loading spinner
  }

  return authenticated ? children : <Navigate to="/login" />;
};

export default ProtectedRoute;
