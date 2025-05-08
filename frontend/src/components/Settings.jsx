import React, { useState, useEffect, useCallback } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "./ui/dialog";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "./ui/tabs";
import { Button } from "./ui/button";
import { supabase } from "../lib/supabase";
import { Info, User, Key, Loader2 } from "lucide-react";
import { useTheme } from "./ui/theme-provider";

const Settings = ({ isOpen, onClose, userId }) => {
  const [activeTab, setActiveTab] = useState("information");
  const [universityUsername, setUniversityUsername] = useState("");
  const [universityPassword, setUniversityPassword] = useState("");
  const [userDisplayName, setUserDisplayName] = useState("");
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState(null);
  const { theme } = useTheme();
  const isLight = theme === "light";

  // Load existing credentials function wrapped in useCallback
  const loadCredentials = useCallback(async () => {
    try {
      // Reset form fields first to avoid showing old data
      setUniversityUsername("");
      setUniversityPassword("");
      setUserDisplayName("");

      const { data, error } = await supabase
        .from("university_credentials")
        .select("university_username, university_password, name")
        .eq("user_id", userId)
        .single();

      if (error && error.code !== "PGRST116") {
        // PGRST116 is "No rows found", which is expected if the user hasn't set credentials yet
        console.error("Error loading credentials:", error);
        return;
      }

      if (data) {
        setUniversityUsername(data.university_username || "");
        setUniversityPassword(data.university_password || "");
        setUserDisplayName(data.name || "");
      }
    } catch (error) {
      console.error("Error in loadCredentials:", error);
    }
  }, [userId]);

  // Load existing credentials when dialog opens
  useEffect(() => {
    if (isOpen) {
      loadCredentials();
    } else {
      // Clear form when dialog closes
      setUniversityUsername("");
      setUniversityPassword("");
      setUserDisplayName("");
      setMessage(null);
    }
  }, [isOpen, loadCredentials]);

  const handleSave = async () => {
    setIsSaving(true);
    setMessage(null);

    try {
      // Use our new endpoint that returns raw login data
      const response = await fetch("http://localhost:8000/ptit-login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          university_username: universityUsername,
          university_password: universityPassword,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(
          errorData.error || "Thông tin đăng nhập không chính xác"
        );
      }

      const data = await response.json();

      if (data.result !== "true") {
        throw new Error(data.error || "Thông tin đăng nhập không chính xác");
      }

      // Extract needed info from the login response
      const {
        name,
        access_token,
        refresh_token,
        ".expires": tokenExpiry,
      } = data;

      // Check if record exists
      const { data: existingData } = await supabase
        .from("university_credentials")
        .select("user_id")
        .eq("user_id", userId)
        .single();

      // Prepare data to save
      const credentialsData = {
        university_username: universityUsername,
        university_password: universityPassword,
        access_token,
        refresh_token,
        token_expiry: new Date(tokenExpiry).toISOString(),
        name,
      };

      if (existingData) {
        // Update existing record
        const { error: updateError } = await supabase
          .from("university_credentials")
          .update(credentialsData)
          .eq("user_id", userId);

        if (updateError) throw updateError;
      } else {
        // Insert new record
        const { error: insertError } = await supabase
          .from("university_credentials")
          .insert([
            {
              user_id: userId,
              ...credentialsData,
            },
          ]);

        if (insertError) throw insertError;
      }

      // Update the display name in the UI
      setUserDisplayName(name);

      setMessage({
        type: "success",
        text: "Xác thực thành công! Thông tin đã được lưu.",
      });
    } catch (error) {
      console.error("Error verifying/saving credentials:", error);
      setMessage({
        type: "error",
        text:
          error.message ||
          "Có lỗi xảy ra khi xác thực thông tin. Vui lòng kiểm tra lại.",
      });
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent
        className={`w-[90%] max-w-[800px] max-h-[80vh] p-0 overflow-hidden ${
          isLight ? "bg-white border-0" : "bg-[#1a1a1a] border-[#d1cfc0]/10"
        }`}
        style={
          isLight
            ? {
                borderRadius: "0.5rem",
                padding: "1px",
                background:
                  "linear-gradient(to right, #6366f1, #8b5cf6, #ec4899)",
              }
            : {}
        }
      >
        <div
          className={`flex h-[500px] ${
            isLight ? "bg-white rounded-[0.45rem]" : ""
          }`}
        >
          {/* Sidebar */}
          <Tabs
            value={activeTab}
            onValueChange={setActiveTab}
            className="flex flex-row h-full w-full"
          >
            <TabsList
              className={`w-48 ${isLight ? "bg-gray-100 text-gray-800" : ""}`}
            >
              <TabsTrigger
                value="information"
                className={`justify-start w-full ${
                  isLight
                    ? "text-gray-800 data-[state=active]:border-l-[3px] data-[state=active]:border-blue-600 data-[state=active]:bg-white data-[state=active]:text-blue-700 data-[state=active]:font-medium"
                    : "data-[state=active]:border-l-[3px] data-[state=active]:border-[#d1cfc0]"
                }`}
              >
                <Info className="mr-2 h-4 w-4" />
                Thông tin PTIT
              </TabsTrigger>
              <TabsTrigger
                value="account"
                className={`justify-start w-full ${
                  isLight
                    ? "text-gray-800 data-[state=active]:border-l-[3px] data-[state=active]:border-blue-600 data-[state=active]:bg-white data-[state=active]:text-blue-700 data-[state=active]:font-medium"
                    : "data-[state=active]:border-l-[3px] data-[state=active]:border-[#d1cfc0]"
                }`}
              >
                <User className="mr-2 h-4 w-4" />
                Tài khoản
              </TabsTrigger>
              <TabsTrigger
                value="security"
                className={`justify-start w-full ${
                  isLight
                    ? "text-gray-800 data-[state=active]:border-l-[3px] data-[state=active]:border-blue-600 data-[state=active]:bg-white data-[state=active]:text-blue-700 data-[state=active]:font-medium"
                    : "data-[state=active]:border-l-[3px] data-[state=active]:border-[#d1cfc0]"
                }`}
              >
                <Key className="mr-2 h-4 w-4" />
                Bảo mật
              </TabsTrigger>
            </TabsList>

            {/* Content */}
            <div className="flex-1 p-6 overflow-y-auto">
              <DialogHeader className="mb-6">
                <DialogTitle
                  className={isLight ? "text-gray-900" : "text-white"}
                >
                  Thiết lập
                </DialogTitle>
              </DialogHeader>

              <TabsContent value="information" className="space-y-6">
                <p
                  className={`text-sm ${
                    isLight ? "text-gray-600" : "text-white/70"
                  }`}
                >
                  Nhập thông tin đăng nhập vào hệ thống trường của bạn để AI có
                  thể truy cập và trả lời các câu hỏi về lịch học, điểm số và
                  các thông tin khác.
                </p>

                <div className="space-y-4">
                  <div>
                    <label
                      htmlFor="userDisplayName"
                      className={`block text-sm font-medium ${
                        isLight ? "text-gray-700" : "text-white/80"
                      }`}
                    >
                      Tên
                    </label>
                    <input
                      type="text"
                      id="userDisplayName"
                      value={userDisplayName}
                      className={`mt-1 block w-full px-3 py-2 rounded-md focus:outline-none focus:ring-2 ${
                        isLight
                          ? "bg-gray-100 border border-gray-300 text-gray-800 placeholder-gray-400 focus:ring-blue-200"
                          : "bg-white/5 border border-white/10 text-white placeholder-white/30 focus:ring-white/20"
                      }`}
                      placeholder="Chưa có thông tin"
                      readOnly
                    />
                  </div>
                  <div>
                    <label
                      htmlFor="universityUsername"
                      className={`block text-sm font-medium ${
                        isLight ? "text-gray-700" : "text-white/80"
                      }`}
                    >
                      Mã số sinh viên
                    </label>
                    <input
                      type="text"
                      id="universityUsername"
                      value={universityUsername}
                      onChange={(e) => setUniversityUsername(e.target.value)}
                      className={`mt-1 block w-full px-3 py-2 rounded-md focus:outline-none focus:ring-2 ${
                        isLight
                          ? "bg-gray-100 border border-gray-300 text-gray-800 placeholder-gray-400 focus:ring-blue-200"
                          : "bg-white/5 border border-white/10 text-white placeholder-white/30 focus:ring-white/20"
                      }`}
                      placeholder="Nhập mã số sinh viên của bạn"
                    />
                  </div>
                  <div>
                    <label
                      htmlFor="universityPassword"
                      className={`block text-sm font-medium ${
                        isLight ? "text-gray-700" : "text-white/80"
                      }`}
                    >
                      Mật khẩu
                    </label>
                    <input
                      type="password"
                      id="universityPassword"
                      value={universityPassword}
                      onChange={(e) => setUniversityPassword(e.target.value)}
                      className={`mt-1 block w-full px-3 py-2 rounded-md focus:outline-none focus:ring-2 ${
                        isLight
                          ? "bg-gray-100 border border-gray-300 text-gray-800 placeholder-gray-400 focus:ring-blue-200"
                          : "bg-white/5 border border-white/10 text-white placeholder-white/30 focus:ring-white/20"
                      }`}
                      placeholder="Nhập mật khẩu trường của bạn"
                    />
                  </div>

                  {message && (
                    <div
                      className={`p-3 rounded-md ${
                        message.type === "success"
                          ? isLight
                            ? "bg-green-100 text-green-800"
                            : "bg-green-500/20 text-green-400"
                          : isLight
                          ? "bg-red-100 text-red-800"
                          : "bg-red-500/20 text-red-400"
                      }`}
                    >
                      {message.text}
                    </div>
                  )}
                </div>

                <div className="flex justify-end mt-8 pt-12">
                  <Button
                    onClick={handleSave}
                    disabled={isSaving}
                    className={
                      isLight
                        ? "bg-blue-600 text-white hover:bg-blue-700 border border-blue-700 py-2 px-6 rounded-md"
                        : "bg-[#2a2a2a] text-[#d1cfc0] hover:bg-[#333333] border border-[#d1cfc0]/20 py-2 px-6 rounded-md"
                    }
                  >
                    {isSaving ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Đang xác thực...
                      </>
                    ) : (
                      "Lưu thông tin"
                    )}
                  </Button>
                </div>
              </TabsContent>

              <TabsContent value="account">
                <h3
                  className={`text-lg font-medium ${
                    isLight ? "text-gray-800" : "text-white"
                  }`}
                >
                  Tài khoản
                </h3>
                <p className={isLight ? "text-gray-600" : "text-white/70"}>
                  Tính năng đang được phát triển.
                </p>
              </TabsContent>

              <TabsContent value="security">
                <h3
                  className={`text-lg font-medium ${
                    isLight ? "text-gray-800" : "text-white"
                  }`}
                >
                  Bảo mật
                </h3>
                <p className={isLight ? "text-gray-600" : "text-white/70"}>
                  Tính năng đang được phát triển.
                </p>
              </TabsContent>
            </div>
          </Tabs>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default Settings;
