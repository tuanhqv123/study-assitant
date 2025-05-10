# StudyAssistant - Nền Tảng Học Tập Tích Hợp Trí Tuệ Nhân Tạo

**Tài Liệu Dự Án**  
**Phiên bản:** 1.0  
**Ngày:** Tháng 5 năm 2025

---

## Tóm Tắt Tổng Quan

StudyAssistant là một nền tảng giáo dục được hỗ trợ bởi trí tuệ nhân tạo, được thiết kế để hỗ trợ sinh viên đại học trong hành trình học tập của họ. Hệ thống tích hợp công nghệ AI tiên tiến với hệ thống dữ liệu của trường đại học để cung cấp cho sinh viên khả năng truy cập tức thì vào thông tin học tập, tài liệu học tập và hỗ trợ học tập cá nhân hóa.

Nền tảng này sử dụng trí tuệ nhân tạo tạo sinh để hiểu và phản hồi các truy vấn của sinh viên bằng ngôn ngữ tự nhiên, đồng thời kết nối với hệ thống của trường đại học để cung cấp thông tin thời gian thực về lịch học, điểm số và tài liệu khóa học. Ngoài ra, hệ thống còn bao gồm các tính năng sáng tạo như tích hợp tìm kiếm web và phân tích tài liệu để nâng cao trải nghiệm học tập.

Tài liệu này cung cấp tổng quan toàn diện về nền tảng StudyAssistant, bao gồm kiến trúc hệ thống, tính năng, công nghệ, thiết kế cơ sở dữ liệu và lộ trình phát triển trong tương lai.

---

## Mục Lục

1. [Tổng Quan Dự Án](#1-tổng-quan-dự-án)
2. [Câu Chuyện Người Dùng](#2-câu-chuyện-người-dùng)
3. [Kiến Trúc Hệ Thống](#3-kiến-trúc-hệ-thống)
4. [Tính Năng Chính](#4-tính-năng-chính)
5. [Công Nghệ Sử Dụng](#5-công-nghệ-sử-dụng)
6. [Cấu Trúc Cơ Sở Dữ Liệu](#6-cấu-trúc-cơ-sở-dữ-liệu)
7. [Chi Tiết Triển Khai](#7-chi-tiết-triển-khai)
8. [Tích Hợp Trí Tuệ Nhân Tạo](#8-tích-hợp-trí-tuệ-nhân-tạo)
9. [Biện Pháp Bảo Mật](#9-biện-pháp-bảo-mật)
10. [Cải Tiến Tương Lai](#10-cải-tiến-tương-lai)
11. [Kết Luận](#11-kết-luận)

---

## 1. Tổng Quan Dự Án

### 1.1 Bối Cảnh

Sinh viên đại học phải đối mặt với nhiều thách thức trong việc quản lý khối lượng học tập, tiếp cận tài liệu khóa học và hiểu các môn học phức tạp. Các hệ thống hỗ trợ giáo dục truyền thống thường thiếu khả năng sẵn sàng ngay lập tức, cá nhân hóa và khả năng tích hợp các nguồn thông tin đa dạng.

StudyAssistant giải quyết những thách thức này bằng cách cung cấp một nền tảng được hỗ trợ bởi AI:

- Trả lời câu hỏi học thuật ngay lập tức
- Cung cấp truy cập thời gian thực vào dữ liệu của trường đại học (lịch học, điểm số)
- Phân tích tài liệu được tải lên để hỗ trợ việc học
- Thực hiện tìm kiếm web để nghiên cứu thêm
- Cung cấp hỗ trợ học tập cá nhân hóa

### 1.2 Mục Tiêu Dự Án

1. Tạo ra sự tích hợp liền mạch giữa công nghệ AI và hệ thống của trường đại học
2. Cung cấp phản hồi chính xác, liên quan đến các truy vấn của sinh viên
3. Cho phép học tập dựa trên tài liệu với phân tích nội dung thông minh
4. Nâng cao khả năng nghiên cứu với tìm kiếm web có mục tiêu
5. Cung cấp giao diện thân thiện với người dùng, dễ tiếp cận cho tất cả sinh viên
6. Đảm bảo tuân thủ bảo mật và quyền riêng tư dữ liệu

### 1.3 Đối Tượng Người Dùng

- Sinh viên đại học (chủ yếu là sinh viên PTIT)
- Giảng viên muốn cung cấp hỗ trợ bổ sung cho sinh viên
- Quản trị viên giáo dục theo dõi nhu cầu và câu hỏi của sinh viên

---

## 2. Câu Chuyện Người Dùng

### Câu Chuyện Người Dùng Sinh Viên

1. **Truy Cập Thông Tin Học Tập**

   - Là một sinh viên, tôi muốn truy cập nhanh lịch học để có thể lên kế hoạch ngày hiệu quả.
   - Là một sinh viên, tôi muốn kiểm tra điểm số mà không cần phải điều hướng qua cổng thông tin phức tạp của trường.
   - Là một sinh viên, tôi muốn biết về các bài tập và thời hạn sắp tới.

2. **Học Tập Hỗ Trợ Bởi AI**

   - Là một sinh viên, tôi muốn đặt câu hỏi về khái niệm khóa học và nhận được giải thích rõ ràng.
   - Là một sinh viên, tôi muốn tải lên ghi chú bài giảng và đặt câu hỏi cụ thể về nội dung.
   - Là một sinh viên, tôi muốn nhận tài liệu học tập bổ sung liên quan đến câu hỏi của tôi.

3. **Hỗ Trợ Nghiên Cứu**

   - Là một sinh viên, tôi muốn tìm kiếm thông tin học thuật mà không cần rời khỏi nền tảng.
   - Là một sinh viên, tôi muốn thấy nguồn đáng tin cậy cho thông tin được cung cấp bởi hệ thống.
   - Là một sinh viên, tôi muốn lưu kết quả tìm kiếm để tham khảo trong tương lai.

4. **Trải Nghiệm Người Dùng**
   - Là một sinh viên, tôi muốn có giao diện trực quan, dễ sử dụng để tương tác với AI.
   - Là một sinh viên, tôi muốn truy cập các cuộc trò chuyện trước đó để xem lại thông tin.
   - Là một sinh viên, tôi muốn sử dụng hệ thống trên cả máy tính để bàn và thiết bị di động.

---

## 3. Kiến Trúc Hệ Thống

StudyAssistant sử dụng kiến trúc hiện đại, có khả năng mở rộng được thiết kế để đảm bảo độ tin cậy, hiệu suất và bảo mật.

### 3.1 Kiến Trúc Tổng Quan

```
┌─────────────┐    ┌──────────────────────────────┐    ┌─────────────────┐
│             │    │                              │    │                 │
│  Frontend   │◄───┤           Backend            │◄───┤   API Bên Ngoài │
│  (React)    │    │          (Python)            │    │                 │
│             │    │                              │    │                 │
└─────────────┘    └──────────────────────────────┘    └─────────────────┘
       ▲                        ▲                              ▲
       │                        │                              │
       │                        ▼                              │
       │            ┌──────────────────────────┐               │
       │            │                          │               │
       └───────────┤        Supabase          ├───────────────┘
                    │ (Cơ sở dữ liệu & Lưu trữ)│
                    │                          │
                    └──────────────────────────┘
```

### 3.2 Luồng Xử Lý Hệ Thống

```
┌───────────────┐
│   Người Dùng  │
└───────┬───────┘
        │
        ▼
┌───────────────┐
│  Gửi Truy Vấn │
└───────┬───────┘
        │
        ▼
┌───────────────────────┐
│  Phân Loại Truy Vấn   │
└───┬─────────┬─────────┘
    │         │         │
    ▼         ▼         ▼
┌─────────┐ ┌─────┐ ┌─────────┐
│ Truy Vấn │ │ Tìm │ │ Upload  │
│ Thông    │ │ Kiếm│ │ Tài Liệu│
│ Thường   │ │ Web │ │         │
└────┬─────┘ └──┬──┘ └────┬────┘
     │          │         │
     │          │         ▼
     │          │    ┌────────────────┐
     │          │    │ Xử Lý &        │
     │          │    │ Vector Embedding│
     │          │    └────────┬───────┘
     │          │             │
     │          │             ▼
     │          │    ┌────────────────┐
     │          │    │ Lưu Trữ Vào    │
     │          │    │ Vector Database│
     │          │    └────────┬───────┘
     │          │             │
     │          │             │
     │          ▼             │
     │     ┌────────────────┐ │
     │     │ Gọi Brave      │ │
     │     │ Search API     │ │
     │     └────────┬───────┘ │
     │              │         │
     │              ▼         │
     │     ┌────────────────┐ │
     │     │ Trích Xuất     │ │
     │     │ Thông Tin Web  │ │
     │     └────────┬───────┘ │
     │              │         │
     ▼              ▼         ▼
┌────────────────────────────────┐
│  Kiểm Tra Phân Loại Sâu Hơn    │
└─────────────┬──────────────────┘
              │
      ┌───────┴───────┐
      │               │
      ▼               ▼
┌──────────┐    ┌────────────┐
│ Lịch Học │    │ Truy Vấn   │
│ (Schedule)│    │ Thông Thường│
└─────┬────┘    └──────┬─────┘
      │                │
      ▼                │
┌──────────┐           │
│ Gọi API  │           │
│ PTIT     │           │
└─────┬────┘           │
      │                │
      ▼                ▼
┌─────────────────────────────┐
│     Xử Lý Bởi AI Model      │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│     Phản Hồi Cho Người Dùng │
└─────────────────────────────┘
```

### 3.3 Phân Tích Thành Phần

1. **Lớp Frontend**

   - Ứng dụng web dựa trên React
   - Thiết kế đáp ứng sử dụng Tailwind CSS
   - Quản lý trạng thái với React context/hooks
   - Định tuyến phía máy khách

2. **Lớp Backend**

   - Máy chủ API Python Flask
   - Dịch vụ xác thực và ủy quyền
   - Tích hợp với dịch vụ AI (OpenRouter)
   - Triển khai logic nghiệp vụ
   - Web scraping và xử lý nội dung

3. **Lớp Cơ Sở Dữ Liệu**

   - Supabase (PostgreSQL)
   - Quản lý dữ liệu người dùng
   - Lưu trữ lịch sử trò chuyện
   - Quản lý tài liệu
   - Vector embeddings cho tìm kiếm ngữ nghĩa

4. **Tích Hợp Bên Ngoài**
   - OpenRouter để truy cập mô hình AI
   - API Trường đại học cho dữ liệu học thuật
   - Brave Search API cho chức năng tìm kiếm web
   - Dịch vụ trích xuất nội dung web

### 3.4 Dịch Vụ Bên Ngoài

- **Truy cập mô hình AI**: OpenRouter API (nhiều mô hình AI)
- **Tìm kiếm Web**: Brave Search API
- **Dữ liệu trường đại học**: Tích hợp PTIT API
- **Trích xuất nội dung**: Dịch vụ web scraper tùy chỉnh

### 3.5 DevOps

- **Quản lý phiên bản**: Git/GitHub
- **Triển khai**: Docker
- **Hosting**: Vercel (frontend), Railway (backend)
- **Giám sát**: Hệ thống ghi log tùy chỉnh

---

## 4. Tính Năng Chính

### 4.1 Giao Diện Trí Tuệ Nhân Tạo Hội Thoại

- Hiểu và tạo ngôn ngữ tự nhiên
- Xử lý hội thoại theo ngữ cảnh
- Hỗ trợ truy vấn học thuật phức tạp
- Hỗ trợ đa ngôn ngữ (Tiếng Việt và Tiếng Anh)
- Phân loại truy vấn thông minh

### 4.2 Tích Hợp Dữ Liệu Trường Đại Học

- Thông tin lịch học thời gian thực
- Truy xuất và hiển thị lịch thi
- Truy xuất và phân tích điểm số
- Truy cập thông tin khóa học và đề cương
- Trình bày dữ liệu học thuật cá nhân hóa
- Quản lý thông tin đăng nhập an toàn

### 4.3 Phân Tích Tài Liệu

- Hỗ trợ nhiều định dạng tài liệu (PDF, DOCX, TXT)
- Phân đoạn thông minh và lập chỉ mục ngữ nghĩa
- Trích xuất nội dung liên quan
- Trả lời câu hỏi dựa trên nội dung tài liệu
- Hệ thống quản lý tài liệu

### 4.4 Tích Hợp Tìm Kiếm Web

- Xây dựng truy vấn thông minh
- Lựa chọn nguồn chất lượng cao
- Trích xuất và tóm tắt nội dung web
- Ghi rõ nguồn và trích dẫn
- Lưu trữ kết quả để tham khảo trong tương lai

### 4.5 Trải Nghiệm Người Dùng

- Giao diện sạch sẽ, tối giản
- Thiết kế đáp ứng cho mọi thiết bị
- Hiển thị markdown cho phản hồi văn bản phong phú
- Định dạng cú pháp mã nguồn
- Quản lý phiên và lịch sử

---

## 5. Công Nghệ Sử Dụng

### 5.1 Công Nghệ Frontend

- **Framework**: React.js
- **Styling**: Tailwind CSS
- **UI Components**: Các component tùy chỉnh với shadcn/ui
- **Quản lý trạng thái**: React Context API
- **HTTP Client**: Axios
- **Chất lượng mã**: ESLint, Prettier

### 5.2 Công Nghệ Backend

- **Framework**: Python Flask
- **API**: Endpoints RESTful
- **Xác thực**: JWT với Supabase Auth
- **Tích hợp AI**: OpenRouter API
- **Web Scraping**: BeautifulSoup, httpx
- **Xử lý văn bản**: Biểu thức chính quy, thuật toán tùy chỉnh
- **Xử lý bất đồng bộ**: asyncio

### 5.3 Cơ Sở Dữ Liệu & Lưu Trữ

- **Cơ sở dữ liệu**: Supabase (PostgreSQL)
- **Lưu trữ tập tin**: Supabase Storage
- **Cơ sở dữ liệu vector**: PostgreSQL với pgvector extension
- **Động cơ truy vấn**: SQL với các hàm chuyên biệt

### 5.4 Dịch Vụ Bên Ngoài

- **Truy cập mô hình AI**: OpenRouter API (nhiều mô hình AI)
- **Tìm kiếm Web**: Brave Search API
- **Dữ liệu trường đại học**: Tích hợp PTIT API
- **Trích xuất nội dung**: Dịch vụ web scraper tùy chỉnh

### 5.5 DevOps

- **Quản lý phiên bản**: Git/GitHub
- **Triển khai**: Docker
- **Hosting**: Vercel (frontend), Railway (backend)
- **Giám sát**: Hệ thống ghi log tùy chỉnh

---

## 6. Cấu Trúc Cơ Sở Dữ Liệu

### 6.1 Sơ Đồ Quan Hệ Thực Thể

```
┌───────────────────┐         ┌────────────────────┐
│   chat_sessions   │         │      messages      │
├───────────────────┤         ├────────────────────┤
│ id (UUID)         │◄────────┤ id (BIGINT)        │
│ user_id (UUID)    │         │ chat_id (UUID)     │
│ created_at        │         │ role               │
│ agent_id          │         │ content            │
└───────────────────┘         │ created_at         │
        ▲                     │ sources (JSONB)    │
        │                     └────────────────────┘
        │
        │
┌───────────────────┐         ┌────────────────────┐         ┌────────────────────┐
│      users        │         │     user_files     │         │    file_chunks     │
├───────────────────┤         ├────────────────────┤         ├────────────────────┤
│ id (UUID)         │◄────────┤ id (UUID)          │◄────────┤ id (UUID)          │
│ email             │         │ user_id (UUID)     │         │ file_id (UUID)     │
│ created_at        │         │ filename           │         │ chunk_index        │
└───────────────────┘         │ content_type       │         │ content            │
        ▲                     │ file_size_bytes    │         │ embedding (VECTOR) │
        │                     │ status             │         │ created_at         │
        │                     │ created_at         │         └────────────────────┘
        │                     └────────────────────┘
        │
┌───────────────────┐
│  university_creds │
├───────────────────┤
│ user_id (UUID)    │
│ univ_username     │
│ univ_password     │
│ access_token      │
│ token_expiry      │
│ name              │
│ refresh_token     │
└───────────────────┘
```

### 6.2 Mô Tả Bảng

#### 6.2.1 Quản Lý Người Dùng

- **users**: Quản lý bởi Supabase Auth, chứa dữ liệu xác thực người dùng
- **university_credentials**: Lưu trữ thông tin đăng nhập được mã hóa để truy cập hệ thống đại học

#### 6.2.2 Hệ Thống Chat

- **chat_sessions**: Đại diện cho các cuộc trò chuyện riêng lẻ
- **messages**: Lưu trữ tất cả tin nhắn trong mỗi phiên chat, bao gồm cả nguồn cho kết quả tìm kiếm web

#### 6.2.3 Quản Lý Tài Liệu

- **user_files**: Metadata cho tài liệu người dùng tải lên
- **file_chunks**: Các đoạn nội dung và vector embeddings cho tìm kiếm ngữ nghĩa

### 6.3 Các Mối Quan Hệ Chính

- Mỗi người dùng có thể có nhiều phiên trò chuyện
- Mỗi phiên trò chuyện chứa nhiều tin nhắn
- Người dùng có thể tải lên nhiều tài liệu
- Mỗi tài liệu được chia thành nhiều đoạn để xử lý
- Thông tin đăng nhập đại học được liên kết trực tiếp với người dùng

---

## 7. Chi Tiết Triển Khai

### 7.1 Kiến Trúc Dịch Vụ Backend

Backend được tổ chức thành các dịch vụ chuyên biệt, mỗi dịch vụ có trách nhiệm cụ thể:

```
app/
├── config/            # Tệp cấu hình và hằng số
├── lib/               # Tích hợp dịch vụ bên ngoài
├── routes/            # Điểm cuối API
├── services/          # Dịch vụ logic nghiệp vụ
│   ├── ai_service.py           # Tích hợp AI và tạo phản hồi
│   ├── file_service.py         # Xử lý và quản lý tài liệu
│   ├── query_classifier.py     # Phân loại loại truy vấn
│   ├── schedule_service.py     # Tích hợp lịch học của trường đại học
│   ├── ptit_auth_service.py    # Xác thực với trường đại học
│   ├── web_search_service.py   # Chức năng tìm kiếm web
│   └── web_scraper_service.py  # Trích xuất nội dung web
└── utils/             # Hàm tiện ích và trợ giúp
```

### 7.2 Luồng Xử Lý Chính

#### 7.2.1 Tìm Kiếm Web và Trích Xuất Nội Dung

1. Người dùng gửi truy vấn cần nghiên cứu
2. Hệ thống phân loại truy vấn là cần tìm kiếm web
3. `web_search_service` gọi Brave Search API để tìm kết quả liên quan
4. Kết quả hàng đầu được gửi đến `web_scraper_service` để trích xuất nội dung
5. Nội dung được xử lý, làm sạch và giới hạn để tránh vượt quá giới hạn token
6. Kết quả tổng hợp được gửi đến AI để xử lý
7. Phản hồi kèm nguồn được trả về cho người dùng và lưu trong cơ sở dữ liệu

#### 7.2.2 Phân Tích Tài Liệu

1. Người dùng tải lên tài liệu qua giao diện
2. `file_service` xử lý tài liệu:
   - Trích xuất nội dung văn bản
   - Chia nội dung thành các đoạn có ngữ nghĩa
   - Tạo vector embeddings cho mỗi đoạn
   - Lưu trữ các đoạn và embeddings trong cơ sở dữ liệu
3. Người dùng đặt câu hỏi về tài liệu
4. Hệ thống thực hiện tìm kiếm tương đồng vector để tìm các đoạn liên quan
5. Các đoạn được truy xuất được gửi đến AI làm ngữ cảnh để trả lời
6. AI phản hồi với thông tin từ tài liệu

#### 7.2.3 Truy Xuất Dữ Liệu Đại Học

1. Người dùng hỏi về lịch học, lịch thi, điểm số hoặc dữ liệu học thuật khác
2. Hệ thống phân loại truy vấn là liên quan đến dữ liệu đại học
3. `ptit_auth_service` xác thực với hệ thống của trường đại học
4. Dịch vụ thích hợp truy xuất dữ liệu được yêu cầu:
   - `schedule_service` xử lý truy vấn về lịch học
   - `exam_schedule_service` xử lý truy vấn về lịch thi
5. Dữ liệu được định dạng và gửi đến AI để trình bày bằng ngôn ngữ tự nhiên
6. AI tạo phản hồi thân thiện với con người kèm theo thông tin được yêu cầu

#### 7.2.4 Xử Lý Lịch Thi

1. Người dùng hỏi về lịch thi của một ngày hoặc tuần cụ thể (ví dụ: "lịch thi tuần sau" hoặc "ngày 20/6 thi môn gì")
2. Hệ thống phân loại truy vấn là liên quan đến lịch thi
3. `exam_schedule_service` sử dụng phương pháp trích xuất thông tin ngày tháng từ `schedule_service`
4. Hệ thống xác định ngày cụ thể hoặc khoảng thời gian (như cả tuần)
5. Dịch vụ truy xuất thông tin lịch thi từ API của trường đại học theo thời gian được yêu cầu
6. Nếu là truy vấn theo tuần, hệ thống sẽ tìm tất cả các kỳ thi trong khoảng thời gian đó
7. Dữ liệu được định dạng và hiển thị với các thông tin chi tiết như:
   - Tên môn thi và mã môn
   - Ngày thi và giờ thi
   - Phòng thi và địa điểm
   - Hình thức thi và thời gian thi
8. AI tạo phản hồi tự nhiên với thông tin lịch thi và lời nhắc về việc chuẩn bị cho kỳ thi

---

## 8. Tích Hợp Trí Tuệ Nhân Tạo

### 8.1 Triển Khai Dịch Vụ AI

Module `ai_service.py` là điểm tích hợp cốt lõi cho chức năng AI, cung cấp:

- Kết nối đến OpenRouter API để truy cập các mô hình AI khác nhau
- Quản lý ngữ cảnh cho các loại truy vấn khác nhau
- Xử lý chuyên biệt cho ngữ cảnh chat, tập tin và tìm kiếm web
- Cơ chế xử lý lỗi và dự phòng
- Định dạng phản hồi và xử lý sau xử lý

### 8.2 Mô Hình AI

Hệ thống sử dụng các mô hình khác nhau thông qua OpenRouter:

- **Mô Hình Chính**: Mistral Small 24B (mistralai/mistral-small-3.1-24b-instruct)
- **Mô Hình Dự Phòng**: Các lựa chọn thay thế khác của OpenRouter

### 8.3 Phân Loại Truy Vấn

Hệ thống thông minh phân loại truy vấn của người dùng để xác định đường dẫn xử lý thích hợp:

- **Kiến Thức Chung**: Được xử lý trực tiếp bởi AI
- **Dữ Liệu Đại Học**: Được chuyển đến API đại học thích hợp
  - **Lịch Học**: Truy vấn về thời khóa biểu lớp học
  - **Lịch Thi**: Truy vấn về lịch thi, kỳ thi, phòng thi
- **Câu Hỏi Tài Liệu**: Được xử lý với ngữ cảnh tài liệu
- **Truy Vấn Tìm Kiếm Web**: Được gửi qua pipeline tìm kiếm và trích xuất
- **Yêu Cầu UML/Sơ Đồ**: Được xử lý với câu nhắc chuyên biệt

### 8.4 Tối Ưu Hóa Nội Dung

Để tối đa hóa chất lượng phản hồi AI trong khi quản lý việc sử dụng token:

- Nội dung web được trích xuất và giới hạn ở 300 ký tự cho mỗi nguồn
- Các đoạn tài liệu được tạo với ranh giới ngữ nghĩa
- Câu nhắc hệ thống được tối ưu hóa cho các loại truy vấn khác nhau
- Định dạng phản hồi đảm bảo tính dễ đọc và hữu ích

---

## 9. Biện Pháp Bảo Mật

### 9.1 Xác Thực & Phân Quyền

- Xác thực dựa trên JWT thông qua Supabase Auth
- Kiểm soát truy cập dựa trên vai trò
- Quản lý phiên và thời gian hết hạn
- Xử lý thông tin đăng nhập an toàn

### 9.2 Bảo Vệ Dữ Liệu

- Thông tin đăng nhập đại học được mã hóa trong cơ sở dữ liệu
- Dữ liệu nhạy cảm không bao giờ được tiết lộ cho frontend
- Lọc và làm sạch nội dung
- Giới hạn tốc độ để ngăn lạm dụng

### 9.3 An Toàn AI

- Phân loại truy vấn để giới hạn phạm vi
- Lọc nội dung cho các yêu cầu không phù hợp
- Câu nhắc hệ thống được thiết kế để ngăn chặn prompt injection
- Xử lý lỗi để ngăn rò rỉ thông tin

---

## 10. Cải Tiến Tương Lai

### 10.1 Lộ Trình Ngắn Hạn (3-6 Tháng)

1. **Nâng Cao Xử Lý Nội Dung Web**

   - Cải thiện thuật toán trích xuất nội dung
   - Tóm tắt nội dung tốt hơn
   - Hỗ trợ các trang web phức tạp hơn

2. **Ứng Dụng Di Động**

   - Ứng dụng di động bản địa cho iOS và Android
   - Thông báo đẩy cho các cập nhật quan trọng
   - Khả năng offline cho truy cập tài liệu

3. **Xử Lý Tài Liệu Nâng Cao**
   - Hỗ trợ thêm định dạng tài liệu (ePub, LaTex)
   - Trích xuất hình ảnh và sơ đồ từ tài liệu
   - Hỗ trợ toán học và công thức

### 10.2 Tầm Nhìn Dài Hạn (6-12 Tháng)

1. **Học Tập Cộng Tác**

   - Không gian tài liệu chia sẻ
   - Trò chuyện nhóm với hỗ trợ AI
   - Đề xuất học tập ngang hàng

2. **Lộ Trình Học Tập Cá Nhân Hóa**

   - Phân tích mẫu hiệu suất sinh viên
   - Đề xuất học tập tùy chỉnh
   - Thích ứng với phong cách học tập

3. **Mở Rộng Tích Hợp Đại Học**
   - Hỗ trợ cho các trường đại học bổ sung
   - Tích hợp với hệ thống quản lý học tập
   - Cổng thông tin dành cho giảng viên để giám sát và hỗ trợ

---

## 11. Kết Luận

StudyAssistant đại diện cho một bước tiến đáng kể trong công nghệ giáo dục, kết hợp khả năng AI, hệ thống dữ liệu đại học và xử lý nội dung nâng cao để tạo ra một trợ lý học tập toàn diện.

Triển khai hiện tại chứng minh tính khả thi và giá trị của phương pháp này, với các tính năng trực tiếp đáp ứng nhu cầu của sinh viên về thông tin học thuật, hỗ trợ học tập và hỗ trợ nghiên cứu. Kiến trúc mô-đun đảm bảo hệ thống có thể tiếp tục phát triển với các khả năng và tích hợp mới.

Khi công nghệ AI tiến bộ và nhu cầu giáo dục phát triển, StudyAssistant được định vị để phát triển thành một công cụ ngày càng có giá trị cho sinh viên và các tổ chức giáo dục, nâng cao trải nghiệm học tập thông qua hỗ trợ thông minh, cá nhân hóa.

---

## Phụ Lục

### Phụ Lục A: Các Điểm Cuối API

| Điểm cuối                 | Phương thức | Mô tả                             |
| ------------------------- | ----------- | --------------------------------- |
| /auth/login               | POST        | Xác thực người dùng               |
| /auth/signup              | POST        | Đăng ký người dùng                |
| /chat                     | POST        | Gửi tin nhắn đến AI               |
| /chat/sessions            | GET         | Liệt kê phiên chat của người dùng |
| /chat/sessions/:id        | GET         | Lấy phiên chat cụ thể             |
| /files/upload             | POST        | Tải lên tài liệu                  |
| /files/list               | GET         | Liệt kê tài liệu của người dùng   |
| /files/:id                | GET         | Lấy chi tiết tài liệu             |
| /university/schedule      | GET         | Lấy lịch học của người dùng       |
| /university/exam-schedule | GET         | Lấy lịch thi của người dùng       |
| /university/grades        | GET         | Lấy điểm số của người dùng        |

### Phụ Lục B: Lược Đồ Cơ Sở Dữ Liệu SQL

```sql
-- Ví dụ lược đồ cho các bảng chính

-- Phiên chat
CREATE TABLE public.chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id),
    created_at TIMESTAMPTZ DEFAULT now(),
    agent_id TEXT
);

-- Tin nhắn
CREATE TABLE public.messages (
    id BIGINT PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    role TEXT,
    content TEXT,
    chat_id UUID REFERENCES public.chat_sessions(id),
    sources JSONB
);

-- Tập tin người dùng
CREATE TABLE public.user_files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id),
    filename TEXT NOT NULL,
    content_type TEXT,
    file_size_bytes BIGINT,
    status TEXT DEFAULT 'processing'::text,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Đoạn tập tin với vector embeddings
CREATE TABLE public.file_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_id UUID NOT NULL REFERENCES public.user_files(id),
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    embedding VECTOR,
    created_at TIMESTAMPTZ DEFAULT now()
);
```
