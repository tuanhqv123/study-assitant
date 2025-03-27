import { createClient } from "@supabase/supabase-js";

const supabaseUrl = "https://hbcwxnllrhlczvaieaiy.supabase.co";
const supabaseKey =
  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhiY3d4bmxscmhsY3p2YWllYWl5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDI2MzA3MTIsImV4cCI6MjA1ODIwNjcxMn0.Rk7dOG6wYsr004TVCyOFVw_6KjG3Dc2BzkXZ-8dYnGg";

export const supabase = createClient(supabaseUrl, supabaseKey);

// Auth functions
export const signInWithGoogle = async () => {
  const { data, error } = await supabase.auth.signInWithOAuth({
    provider: "google",
    options: {
      redirectTo: window.location.origin,
    },
  });
  return { data, error };
};

export const signUpWithEmail = async (email, password) => {
  const { data, error } = await supabase.auth.signUp({
    email,
    password,
    options: {
      emailRedirectTo: window.location.origin,
    },
  });
  return { data, error };
};

export const signInWithEmail = async (email, password) => {
  const { data, error } = await supabase.auth.signInWithPassword({
    email,
    password,
  });
  return { data, error };
};

export const sendOTP = async (email) => {
  try {
    const { data, error } = await supabase.auth.signInWithOtp({
      email,
      options: {
        emailRedirectTo: window.location.origin,
      },
    });

    return { data, error };
  } catch (error) {
    // Prevent rate limit errors from breaking the flow
    if (error.message.includes("rate limit")) {
      return { data: null, error: null };
    }
    throw error;
  }
};

export const verifyOTP = async (email, token, type = "email") => {
  const { data, error } = await supabase.auth.verifyOtp({
    email,
    token,
    type,
  });
  return { data, error };
};

export const getSession = async () => {
  const { data, error } = await supabase.auth.getSession();
  return { data, error };
};

export const signOut = async () => {
  const { error } = await supabase.auth.signOut();
  return { error };
};

export const onAuthStateChange = (callback) => {
  return supabase.auth.onAuthStateChange(callback);
};
