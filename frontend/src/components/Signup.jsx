import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { signUpWithEmail, sendOTP, verifyOTP } from "../lib/supabase";

const Signup = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [otp, setOtp] = useState("");
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [step, setStep] = useState(1); // 1: Đăng ký, 2: Xác thực OTP

  const handleSignup = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      if (step === 1) {
        // Kiểm tra mật khẩu khớp
        if (password !== confirmPassword) {
          throw new Error("Mật khẩu không khớp");
        }

        // Đăng ký tài khoản
        const { error: signupError } = await signUpWithEmail(email, password);
        if (signupError) throw signupError;

        // Gửi OTP xác thực
        try {
          await sendOTP(email);
          // eslint-disable-next-line no-unused-vars
        } catch (otpError) {
          // Ignore rate limit errors - email has likely been sent anyway
        }

        // Always move to step 2 after signup
        setStep(2);
      } else {
        // Xác thực OTP
        const { error } = await verifyOTP(email, otp, "signup");
        if (error) throw error;
        navigate("/login");
      }
    } catch (error) {
      setError(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleResendOTP = async () => {
    try {
      setIsLoading(true);
      setError(null);
      await sendOTP(email);
      setError("Đã gửi lại mã xác thực tới email của bạn");
    } catch (error) {
      // Only show non-rate limit errors
      if (!error.message.includes("rate limit")) {
        setError(error.message);
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-black/95 flex items-center justify-center">
      <div className="bg-secondary p-8 rounded-lg w-full max-w-md">
        <h1 className="text-2xl font-bold text-white mb-6">Đăng ký</h1>

        {error && <div className="text-red-500 text-sm mb-4">{error}</div>}

        {step === 1 ? (
          <form onSubmit={handleSignup} className="space-y-4">
            <div>
              <label
                htmlFor="email"
                className="block text-sm font-medium text-white/80"
              >
                Email
              </label>
              <input
                type="email"
                id="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="mt-1 block w-full px-3 py-2 bg-white/5 border border-white/10 rounded-md text-white placeholder-white/30 focus:outline-none focus:ring-2 focus:ring-white/20"
                placeholder="Nhập email của bạn"
                required
              />
            </div>
            <div>
              <label
                htmlFor="password"
                className="block text-sm font-medium text-white/80"
              >
                Mật khẩu
              </label>
              <input
                type="password"
                id="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="mt-1 block w-full px-3 py-2 bg-white/5 border border-white/10 rounded-md text-white placeholder-white/30 focus:outline-none focus:ring-2 focus:ring-white/20"
                placeholder="Nhập mật khẩu"
                required
              />
            </div>
            <div>
              <label
                htmlFor="confirmPassword"
                className="block text-sm font-medium text-white/80"
              >
                Xác nhận mật khẩu
              </label>
              <input
                type="password"
                id="confirmPassword"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="mt-1 block w-full px-3 py-2 bg-white/5 border border-white/10 rounded-md text-white placeholder-white/30 focus:outline-none focus:ring-2 focus:ring-white/20"
                placeholder="Nhập lại mật khẩu"
                required
              />
            </div>
            <button
              type="submit"
              disabled={isLoading}
              className="w-full px-4 py-2 bg-white/10 text-white rounded-md hover:bg-white/20 focus:outline-none focus:ring-2 focus:ring-white/20"
            >
              {isLoading ? "Đang xử lý..." : "Tiếp tục"}
            </button>
          </form>
        ) : (
          <form onSubmit={handleSignup} className="space-y-4">
            <div>
              <label
                htmlFor="otp"
                className="block text-sm font-medium text-white/80"
              >
                Mã xác nhận
              </label>
              <p className="text-white/60 text-xs mb-2">
                Đã gửi mã xác nhận đến email của bạn
              </p>
              <input
                type="text"
                id="otp"
                value={otp}
                onChange={(e) => setOtp(e.target.value)}
                className="mt-1 block w-full px-3 py-2 bg-white/5 border border-white/10 rounded-md text-white placeholder-white/30 focus:outline-none focus:ring-2 focus:ring-white/20"
                placeholder="Nhập mã xác nhận từ email"
                required
              />
            </div>
            <button
              type="submit"
              disabled={isLoading}
              className="w-full px-4 py-2 bg-white/10 text-white rounded-md hover:bg-white/20 focus:outline-none focus:ring-2 focus:ring-white/20"
            >
              {isLoading ? "Đang xác thực..." : "Xác thực"}
            </button>
            <button
              type="button"
              onClick={handleResendOTP}
              disabled={isLoading}
              className="text-white/60 text-sm hover:text-white underline"
            >
              Gửi lại mã
            </button>
          </form>
        )}

        <div className="mt-4 text-center">
          <button
            onClick={() => navigate("/login")}
            className="text-white/80 hover:text-white"
          >
            Đã có tài khoản? Đăng nhập
          </button>
        </div>
      </div>
    </div>
  );
};

export default Signup;
