import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  signInWithGoogle,
  signInWithEmail,
  sendOTP,
  verifyOTP,
} from "../lib/supabase";
import { useTheme } from "./ui/theme-provider";

const Login = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [otp, setOtp] = useState("");
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [step, setStep] = useState(1); // 1: Đăng nhập, 2: Xác thực OTP
  const { theme } = useTheme();
  const isLight = theme === "light";

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
    <div
      className={`min-h-screen ${
        isLight ? "bg-gray-50" : "bg-black/95"
      } flex items-center justify-center`}
    >
      <div
        className={`${
          isLight ? "bg-white shadow-md border border-gray-200" : "bg-secondary"
        } p-8 rounded-lg w-full max-w-md`}
      >
        <h1
          className={`text-2xl font-bold ${
            isLight ? "text-gray-900" : "text-white"
          } mb-6`}
        >
          Đăng nhập
        </h1>

        {error && <div className="text-red-500 text-sm mb-4">{error}</div>}

        <button
          onClick={handleLoginWithGoogle}
          disabled={isLoading}
          className={`w-full px-4 py-2 ${
            isLight
              ? "bg-gray-100 text-gray-800 hover:bg-gray-200 focus:ring-gray-300"
              : "bg-white/10 text-white hover:bg-white/20 focus:ring-white/20"
          } rounded-md focus:outline-none focus:ring-2 mb-4`}
        >
          {isLoading ? "Đang xử lý..." : "Đăng nhập với Google"}
        </button>

        <div
          className={`text-center ${
            isLight ? "text-gray-600" : "text-white/80"
          } mb-4`}
        >
          hoặc
        </div>

        {step === 1 ? (
          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label
                htmlFor="email"
                className={`block text-sm font-medium ${
                  isLight ? "text-gray-700" : "text-white/80"
                }`}
              >
                Email
              </label>
              <input
                type="email"
                id="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className={`mt-1 block w-full px-3 py-2 rounded-md focus:outline-none focus:ring-2 ${
                  isLight
                    ? "bg-gray-100 border border-gray-300 text-gray-800 placeholder-gray-400 focus:ring-blue-200"
                    : "bg-white/5 border border-white/10 text-white placeholder-white/30 focus:ring-white/20"
                }`}
                placeholder="Nhập email của bạn"
                required
              />
            </div>
            <div>
              <label
                htmlFor="password"
                className={`block text-sm font-medium ${
                  isLight ? "text-gray-700" : "text-white/80"
                }`}
              >
                Mật khẩu
              </label>
              <input
                type="password"
                id="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className={`mt-1 block w-full px-3 py-2 rounded-md focus:outline-none focus:ring-2 ${
                  isLight
                    ? "bg-gray-100 border border-gray-300 text-gray-800 placeholder-gray-400 focus:ring-blue-200"
                    : "bg-white/5 border border-white/10 text-white placeholder-white/30 focus:ring-white/20"
                }`}
                placeholder="Nhập mật khẩu"
              />
            </div>
            <button
              type="submit"
              disabled={isLoading}
              className={`w-full px-4 py-2 rounded-md focus:outline-none focus:ring-2 ${
                isLight
                  ? "bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-300"
                  : "bg-white/10 text-white hover:bg-white/20 focus:ring-white/20"
              }`}
            >
              {isLoading ? "Đang xử lý..." : "Đăng nhập"}
            </button>
          </form>
        ) : (
          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label
                htmlFor="otp"
                className={`block text-sm font-medium ${
                  isLight ? "text-gray-700" : "text-white/80"
                }`}
              >
                Mã OTP
              </label>
              <input
                type="text"
                id="otp"
                value={otp}
                onChange={(e) => setOtp(e.target.value)}
                className={`mt-1 block w-full px-3 py-2 rounded-md focus:outline-none focus:ring-2 ${
                  isLight
                    ? "bg-gray-100 border border-gray-300 text-gray-800 placeholder-gray-400 focus:ring-blue-200"
                    : "bg-white/5 border border-white/10 text-white placeholder-white/30 focus:ring-white/20"
                }`}
                placeholder="Nhập mã OTP từ email"
                required
              />
            </div>
            <button
              type="submit"
              disabled={isLoading}
              className={`w-full px-4 py-2 rounded-md focus:outline-none focus:ring-2 ${
                isLight
                  ? "bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-300"
                  : "bg-white/10 text-white hover:bg-white/20 focus:ring-white/20"
              }`}
            >
              {isLoading ? "Đang xác thực..." : "Xác thực OTP"}
            </button>
          </form>
        )}

        <div className="mt-4 text-center">
          <button
            onClick={() => navigate("/signup")}
            className={`${
              isLight
                ? "text-blue-600 hover:text-blue-800"
                : "text-white/80 hover:text-white"
            }`}
          >
            Chưa có tài khoản? Đăng ký
          </button>
        </div>
      </div>
    </div>
  );
};

export default Login;
