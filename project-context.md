# Study Assistant Chatbot: Project Context

## 1. Project Overview

Study Assistant là một ứng dụng web chatbot AI hỗ trợ sinh viên với các vấn đề học tập. Ứng dụng sẽ:

- Cung cấp một giao diện chat đơn giản để sinh viên tương tác
- Sử dụng AI (thông qua OpenRouter API) để trả lời các câu hỏi học tập
- Kết nối với API của nhà trường để lấy dữ liệu thực của sinh viên
- Cung cấp thông tin về lịch học, điểm số, danh sách môn học
- Tư vấn về sự nghiệp và định hướng học tập

## 2. Đối tượng người dùng

- Sinh viên đại học cần hỗ trợ học tập

## 3. Kiến trúc hệ thống

Hệ thống sẽ được xây dựng với kiến trúc client-server:

- **Frontend**: React với Tailwind CSS, giao diện đơn giản và thân thiện
- **Backend**: Python với FastAPI, xử lý logic nghiệp vụ và tích hợp API
- **Bảo mật**: JWT authentication, mã hóa dữ liệu nhạy cảm
- **Tích hợp API**: OpenRouter API (AI), University API (dữ liệu sinh viên)
- **Cơ sở dữ liệu**: Supabase (lưu trữ lịch sử chat, tùy chỉnh người dùng)

## 4. Công nghệ sử dụng

### Frontend

- **Framework**: React.js với TypeScript
- **Styling**: Tailwind CSS
- **State Management**: Redux Toolkit
- **Routing**: React Router
- **HTTP Client**: Axios

### Backend

- **Framework**: Python với FastAPI
- **Authentication**: JWT tokens, OAuth 2.0
- **Database**: Supabase (PostgreSQL)
- **API Integration**: Python Requests/httpx
- **Async Processing**: asyncio/uvicorn

### DevOps

- **Version Control**: Git/GitHub
- **Deployment**: Docker, Vercel (frontend), Railway (backend)
- **CI/CD**: GitHub Actions
- **Monitoring**: Sentry

## 5. Tính năng chính

### 5.1 Đăng nhập và xác thực

- Đăng nhập bằng mã số sinh viên (MSSV) và mật khẩu
- Phiên làm việc sử dụng JWT
- Xác thực thông qua API của trường

### 5.2 Giao diện chat

- Giao diện đơn giản, thân thiện với người dùng
- Hỗ trợ hiển thị markdown
- Lưu trữ lịch sử chat
- Hiệu ứng đang nhập (typing indicator)

### 5.3 Truy vấn dữ liệu sinh viên

- Xem lịch học theo ngày/tuần/tháng
- Tra cứu điểm số theo học kỳ/năm học
- Tìm kiếm thông tin về môn học
- Lọc và sắp xếp dữ liệu

### 5.4 Tư vấn học tập

- Phân tích kết quả học tập
- Gợi ý cải thiện điểm số
- Đề xuất lộ trình học tập
- Tư vấn định hướng nghề nghiệp

### 5.5 Bảo mật và an toàn

- Mã hóa dữ liệu nhạy cảm
- Hạn chế prompt injection
- Lọc nội dung không phù hợp
- Giới hạn phạm vi câu hỏi trong lĩnh vực học tập

## 6. Quy trình sử dụng ứng dụng

1. Sinh viên đăng nhập bằng MSSV và mật khẩu
2. Hệ thống xác thực và lấy dữ liệu cơ bản từ API trường
3. Giao diện chat được hiển thị với tin nhắn chào mừng
4. Sinh viên đặt câu hỏi về lịch học, điểm số, hoặc tư vấn học tập
5. Hệ thống phân tích câu hỏi và:
   - Nếu là câu hỏi về dữ liệu cá nhân → Truy vấn API trường
   - Nếu là câu hỏi tư vấn → Sử dụng AI để phân tích và đưa ra lời khuyên
6. Kết quả được hiển thị trong giao diện chat
7. Lịch sử chat được lưu trữ cho các phiên sau

## 7. Kế hoạch triển khai

### 7.1 Giai đoạn 1: Thiết lập cơ bản (3 tuần)

- Tạo repository và cấu trúc dự án
- Xây dựng frontend cơ bản (trang đăng nhập, giao diện chat)
- Thiết lập backend với xác thực cơ bản
- Tích hợp với API trường cho đăng nhập

### 7.2 Giai đoạn 2: Tích hợp dữ liệu (3 tuần)

- Tích hợp API trường để lấy lịch học
- Tích hợp API trường để lấy điểm số
- Tích hợp API trường để tìm kiếm thông tin môn học
- Xây dựng các component hiển thị dữ liệu

### 7.3 Giai đoạn 3: Tích hợp AI (3 tuần)

- Thiết lập kết nối với OpenRouter API
- Xây dựng hệ thống prompt engineering
- Triển khai các biện pháp bảo mật cho AI
- Tối ưu hóa độ chính xác của phản hồi

### 7.4 Giai đoạn 4: Hoàn thiện và triển khai (3 tuần)

- Kiểm thử toàn diện
- Tối ưu hóa hiệu suất
- Triển khai môi trường production
- Thu thập phản hồi và cải tiến

## 8. Thách thức kỹ thuật và giải pháp

### 8.1 Bảo mật

**Thách thức:** Bảo vệ thông tin nhạy cảm của sinh viên.
**Giải pháp:**

- JWT cho xác thực
- Mã hóa dữ liệu nhạy cảm
- Phiên làm việc có thời hạn
- Giới hạn quyền truy cập

### 8.2 Tích hợp API trường

**Thách thức:** Đảm bảo tính ổn định và hiệu suất khi tích hợp với API bên ngoài.
**Giải pháp:**

- Caching dữ liệu
- Retry mechanism
- Error handling
- Rate limiting

### 8.3 AI Safety

**Thách thức:** Ngăn chặn prompt injection và đảm bảo AI không trả lời các câu hỏi không phù hợp.
**Giải pháp:**

- Sử dụng system prompt chặt chẽ
- Lọc nội dung đầu vào
- Phát hiện và ngăn chặn những nỗ lực thay đổi hướng AI
- Giới hạn phạm vi câu hỏi trong lĩnh vực học tập

### 8.4 UX/UI

**Thách thức:** Tạo giao diện đơn giản nhưng hiệu quả.
**Giải pháp:**

- Thiết kế tối giản
- Tối ưu hóa cho thiết bị di động
- Thời gian phản hồi nhanh
- Visual feedback rõ ràng

## 9. Đánh giá hiệu quả

Dự án sẽ được đánh giá dựa trên các chỉ số:

- **Độ chính xác của thông tin:** % thông tin được cung cấp chính xác
- **Thời gian phản hồi:** Thời gian trung bình để trả lời câu hỏi
- **Mức độ hài lòng người dùng:** Từ phản hồi và đánh giá
- **Tỷ lệ sử dụng lại:** % người dùng quay lại sử dụng dịch vụ
- **Khả năng mở rộng:** Dễ dàng thêm tính năng mới

## 10. Mở rộng tương lai

- **Chatbot thông minh hơn:** Sử dụng mô hình AI tiên tiến hơn
- **Hỗ trợ nhiều ngôn ngữ:** Thêm tiếng Anh và các ngôn ngữ khác
- **Tích hợp thêm dịch vụ:** Đăng ký môn học, yêu cầu giấy tờ
- **Ứng dụng di động:** Phát triển phiên bản native cho iOS/Android
- **Hệ thống gợi ý cá nhân hóa:** Dựa trên lịch sử học tập để đưa ra gợi ý
- **Tích hợp với các nền tảng học tập:** LMS, Google Classroom, v.v.

## 11. Lưu trữ và xử lý chat với Supabase

### 11.1 Cấu trúc dữ liệu đơn giản

Supabase sẽ được sử dụng với cấu trúc đơn giản để hỗ trợ chức năng chính: phân loại câu hỏi và truy xuất dữ liệu trường. Chúng ta sẽ thiết kế hai bảng chính:

#### Bảng `users`

```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  student_id VARCHAR NOT NULL UNIQUE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  last_login TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### Bảng `chat_messages`

```sql
CREATE TABLE chat_messages (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  question TEXT NOT NULL,
  answer TEXT NOT NULL,
  question_type VARCHAR NOT NULL, -- 'schedule', 'grades', 'courses', 'general'
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index để truy vấn nhanh
CREATE INDEX idx_chat_messages_user_id ON chat_messages(user_id);
CREATE INDEX idx_chat_messages_created_at ON chat_messages(created_at);
```

### 11.2 Quy trình xử lý câu hỏi

Quy trình xử lý chat sẽ đơn giản và trực tiếp:

1. **Phân loại câu hỏi**: Khi sinh viên gửi câu hỏi, hệ thống sẽ phân loại câu hỏi đó thuộc loại nào:

   - Lịch học (`schedule`)
   - Điểm số (`grades`)
   - Thông tin môn học (`courses`)
   - Câu hỏi chung (`general`)

2. **Xử lý câu hỏi dữ liệu trường**:

   - Nếu câu hỏi liên quan đến dữ liệu trường (lịch học, điểm số, môn học)
   - Hệ thống sẽ sử dụng thông tin đăng nhập (MSSV, mật khẩu) đã lưu trong phiên
   - Gọi API trường tương ứng để lấy dữ liệu
   - Truyền dữ liệu vào AI để xử lý câu trả lời

3. **Xử lý câu hỏi tư vấn chung**:

   - Nếu là câu hỏi tư vấn học tập hoặc sự nghiệp
   - Gửi trực tiếp đến AI để trả lời

4. **Lưu trữ đơn giản**:
   - Lưu câu hỏi và câu trả lời vào bảng `chat_messages`
   - Lưu loại câu hỏi để phân tích sau này
   - Không cần quản lý phức tạp về cuộc hội thoại hay metadata

### 11.3 Ví dụ về luồng xử lý

```python
async def process_question(user_id, question):
    # 1. Phân loại câu hỏi
    question_type = classify_question(question)

    # 2. Xử lý dựa trên loại câu hỏi
    if question_type in ['schedule', 'grades', 'courses']:
        # Lấy thông tin đăng nhập từ phiên
        credentials = get_user_credentials(user_id)

        # Gọi API trường tương ứng
        if question_type == 'schedule':
            data = await university_api.get_schedule(credentials)
        elif question_type == 'grades':
            data = await university_api.get_grades(credentials)
        elif question_type == 'courses':
            data = await university_api.get_courses(credentials)

        # Gửi câu hỏi và dữ liệu đến AI
        answer = await ai_service.get_answer(question, data)
    else:
        # Câu hỏi chung - gửi trực tiếp đến AI
        answer = await ai_service.get_answer(question)

    # 3. Lưu câu hỏi và câu trả lời
    await store_message(user_id, question, answer, question_type)

    return answer
```

### 11.4 Hàm phân loại câu hỏi

```python
def classify_question(question):
    # Các từ khóa để phân loại câu hỏi
    schedule_keywords = ['lịch học', 'thời khóa biểu', 'lịch thi', 'khi nào học']
    grades_keywords = ['điểm', 'điểm số', 'gpa', 'kết quả học tập']
    courses_keywords = ['môn học', 'khóa học', 'tín chỉ', 'học phần']

    question_lower = question.lower()

    if any(keyword in question_lower for keyword in schedule_keywords):
        return 'schedule'
    elif any(keyword in question_lower for keyword in grades_keywords):
        return 'grades'
    elif any(keyword in question_lower for keyword in courses_keywords):
        return 'courses'
    else:
        return 'general'
```

### 11.5 Lưu trữ tin nhắn

```python
async def store_message(user_id, question, answer, question_type):
    data = {
        "user_id": user_id,
        "question": question,
        "answer": answer,
        "question_type": question_type
    }

    # Lưu vào Supabase
    response = supabase.table("chat_messages").insert(data).execute()
    return response.data
```

### 11.6 Ưu điểm của cách tiếp cận đơn giản

1. **Tập trung vào chức năng chính**: Phân loại câu hỏi và tích hợp API trường
2. **Đơn giản trong triển khai**: Ít bảng, ít logic phức tạp
3. **Dễ bảo trì**: Cấu trúc đơn giản, dễ hiểu và sửa chữa
4. **Hiệu suất tốt**: Ít phụ thuộc vào cơ sở dữ liệu phức tạp
5. **Mở rộng dễ dàng**: Có thể dễ dàng thêm loại câu hỏi mới
