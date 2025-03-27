import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  signInWithGoogle,
  signInWithEmail,
  sendOTP,
  verifyOTP,
} from "../lib/supabase";

const Login = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [otp, setOtp] = useState("");
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [step, setStep] = useState(1); // 1: Đăng nhập, 2: Xác thực OTP

  const handleLoginWithGoogle = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const { error } = await signInWithGoogle();
      if (error) throw error;
      navigate("/chat");
    } catch (error) {
      setError(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      // Bước 1: Đăng nhập bằng email/mật khẩu hoặc gửi OTP
      if (step === 1) {
        if (password) {
          const { error } = await signInWithEmail(email, password);
          if (error) throw error;
          navigate("/chat");
        } else {
          const { error } = await sendOTP(email);
          if (error) throw error;
          setStep(2);
        }
      }
      // Bước 2: Xác thực OTP
      else {
        const { error } = await verifyOTP(email, otp);
        if (error) throw error;
        navigate("/chat");
      }
    } catch (error) {
      setError(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-black/95 flex items-center justify-center">
      <div className="bg-secondary p-8 rounded-lg w-full max-w-md">
        <h1 className="text-2xl font-bold text-white mb-6">Đăng nhập</h1>

        {error && <div className="text-red-500 text-sm mb-4">{error}</div>}

        <button
          onClick={handleLoginWithGoogle}
          disabled={isLoading}
          className="w-full px-4 py-2 bg-white/10 text-white rounded-md hover:bg-white/20 focus:outline-none focus:ring-2 focus:ring-white/20 mb-4"
        >
          {isLoading ? "Đang xử lý..." : "Đăng nhập với Google"}
        </button>

        <div className="text-center text-white/80 mb-4">hoặc</div>

        {step === 1 ? (
          <form onSubmit={handleLogin} className="space-y-4">
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
              />
            </div>
            <button
              type="submit"
              disabled={isLoading}
              className="w-full px-4 py-2 bg-white/10 text-white rounded-md hover:bg-white/20 focus:outline-none focus:ring-2 focus:ring-white/20"
            >
              {isLoading ? "Đang xử lý..." : "Đăng nhập"}
            </button>
          </form>
        ) : (
          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label
                htmlFor="otp"
                className="block text-sm font-medium text-white/80"
              >
                Mã OTP
              </label>
              <input
                type="text"
                id="otp"
                value={otp}
                onChange={(e) => setOtp(e.target.value)}
                className="mt-1 block w-full px-3 py-2 bg-white/5 border border-white/10 rounded-md text-white placeholder-white/30 focus:outline-none focus:ring-2 focus:ring-white/20"
                placeholder="Nhập mã OTP từ email"
                required
              />
            </div>
            <button
              type="submit"
              disabled={isLoading}
              className="w-full px-4 py-2 bg-white/10 text-white rounded-md hover:bg-white/20 focus:outline-none focus:ring-2 focus:ring-white/20"
            >
              {isLoading ? "Đang xác thực..." : "Xác thực OTP"}
            </button>
          </form>
        )}

        <div className="mt-4 text-center">
          <button
            onClick={() => navigate("/signup")}
            className="text-white/80 hover:text-white"
          >
            Chưa có tài khoản? Đăng ký
          </button>
        </div>
      </div>
    </div>
  );
};

export default Login;
