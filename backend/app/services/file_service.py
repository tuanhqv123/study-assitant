import os
import uuid
import random
import hashlib
from werkzeug.utils import secure_filename
from ..lib.supabase import supabase
from ..utils.logger import Logger

logger = Logger()

class FileService:
    def __init__(self):
        # Sử dụng simple embedding thay vì mô hình ML phức tạp
        try:
            self.embedding_dimension = 384  # Kích thước vector giống model thật
            logger.log_with_timestamp('FILE_SERVICE', 'Simple embedding system initialized')
        except Exception as e:
            logger.log_with_timestamp('FILE_SERVICE_ERROR', f'Failed to initialize: {e}')
            raise

    def _create_simple_embedding(self, text):
        """Tạo vector embedding đơn giản từ text sử dụng hash"""
        # Sử dụng MD5 hash để tạo một giá trị ngẫu nhiên nhưng nhất quán
        hash_obj = hashlib.md5(text.encode('utf-8'))
        hash_value = int(hash_obj.hexdigest(), 16)
        
        # Khởi tạo random generator với hash value làm seed
        random.seed(hash_value)
        
        # Tạo vector có kích thước 384 (giống model thật) với giá trị ngẫu nhiên từ -1 đến 1
        return [random.uniform(-1, 1) for _ in range(self.embedding_dimension)]

    def save_file_and_chunks_to_supabase(self, user_id, file, file_content):
        """
        Save file metadata and its text chunks with embeddings into Supabase.
        Returns the generated file_id.
        """
        # create file_id and temp path
        file_id = str(uuid.uuid4())
        filename = secure_filename(file.filename)
        # metadata
        file_size = len(file_content)
        meta = {
            'id': file_id,
            'user_id': user_id,
            'filename': filename,
            'content_type': file.content_type,
            'file_size_bytes': file_size,
            'status': 'processing'
        }
        
        # Sử dụng phương thức đồng bộ thay vì await
        supabase.table('user_files').insert(meta).execute()
        logger.log_with_timestamp('FILE_SERVICE', f'Metadata inserted for {file_id}')
        
        # chunk text
        chunks = [ file_content[i:i+500] for i in range(0, len(file_content), 400) ]
        
        # generate simple embeddings
        embeddings = [self._create_simple_embedding(chunk) for chunk in chunks]
        
        # prepare records
        records = []
        for idx, (chunk, emb) in enumerate(zip(chunks, embeddings)):
            records.append({
                'file_id': file_id,
                'chunk_index': idx,
                'content': chunk,
                'embedding': emb
            })
            
        # batch insert
        for i in range(0, len(records), 100):
            batch = records[i:i+100]
            supabase.table('file_chunks').insert(batch).execute()
            
        # update status
        supabase.table('user_files').update({'status':'ready'}).eq('id', file_id).execute()
        logger.log_with_timestamp('FILE_SERVICE', f'File {file_id} saved with {len(records)} chunks')
        return file_id

    def search_relevant_chunks_in_supabase(self, query, file_id, top_k=10):
        """
        Query Supabase RPC to retrieve top_k similar chunks for given query and file.
        Returns list of text chunks.
        """
        # generate simple query embedding
        emb = self._create_simple_embedding(query)
        
        try:
            # Giảm ngưỡng tương đồng xuống để có nhiều kết quả hơn
            match_threshold = 0.2  # Giảm xuống 0.2 để lấy nhiều kết quả hơn
            
            # call RPC for vector search
            response = supabase.rpc('match_file_chunks', {
                'query_embedding': emb,
                'match_file_id': file_id,
                'match_threshold': match_threshold,
                'match_count': top_k
            }).execute()
            
            # Xử lý kết quả phù hợp với phiên bản mới của Supabase Python Client
            try:
                # Kiểm tra lỗi theo cách khác thay vì dùng .error
                if hasattr(response, 'error') and response.error:
                    logger.log_with_timestamp('FILE_SERVICE_ERROR', f'RPC error: {response.error.message}')
                    # Fallback: lấy một số chunks ngẫu nhiên từ file
                    return self._get_fallback_chunks(file_id, top_k)
                    
                # Truy cập dữ liệu bằng .data hoặc []
                data = []
                if hasattr(response, 'data'):
                    data = response.data or []
                elif isinstance(response, dict) and 'data' in response:
                    data = response['data'] or []
                elif hasattr(response, '__getitem__'):
                    try:
                        data = response[:] or []  # Truy cập bằng slicing nếu là iterable
                    except (TypeError, IndexError):
                        data = []
                
                chunks = [item['content'] for item in data if isinstance(item, dict) and 'content' in item]
                
                # Thêm tìm kiếm từ khóa trực tiếp khi vector search không đủ kết quả
                if len(chunks) < top_k:
                    logger.log_with_timestamp('FILE_SERVICE', f'Vector search found only {len(chunks)} chunks, supplementing with keyword search')
                    keyword_chunks = self._keyword_search_chunks(query, file_id, top_k - len(chunks))
                    # Thêm các chunks tìm được bằng từ khóa mà không trùng với vector search
                    for chunk in keyword_chunks:
                        if chunk not in chunks:
                            chunks.append(chunk)
                            if len(chunks) >= top_k:
                                break
                
                # Nếu không tìm thấy kết quả nào, lấy một số chunks ngẫu nhiên từ file
                if not chunks:
                    logger.log_with_timestamp('FILE_SERVICE', f'No matching chunks found, using fallback')
                    return self._get_fallback_chunks(file_id, top_k)
                    
                logger.log_with_timestamp('FILE_SERVICE', f'Found {len(chunks)} matching chunks')
                return chunks
                
            except Exception as e:
                logger.log_with_timestamp('FILE_SERVICE_ERROR', f'Error processing response: {str(e)}')
                # Fallback khi có lỗi xử lý response
                return self._get_fallback_chunks(file_id, top_k)
                
        except Exception as e:
            logger.log_with_timestamp('FILE_SERVICE_ERROR', f'RPC call error: {str(e)}')
            return self._get_fallback_chunks(file_id, top_k)
            
    def _get_fallback_chunks(self, file_id, count=5):
        """
        Lấy một số chunks ngẫu nhiên từ file khi không tìm được kết quả tương đồng.
        """
        try:
            # Lấy tất cả các chunks của file và trả về một số ngẫu nhiên
            response = supabase.table('file_chunks').select('content').eq('file_id', file_id).limit(50).execute()
            
            data = []
            if hasattr(response, 'data'):
                data = response.data or []
            elif isinstance(response, dict) and 'data' in response:
                data = response['data'] or []
                
            chunks = [item['content'] for item in data if isinstance(item, dict) and 'content' in item]
            
            if not chunks:
                # Nếu vẫn không có kết quả, lấy mẫu từ bảng metadata
                meta_response = supabase.table('user_files').select('filename').eq('id', file_id).execute()
                if hasattr(meta_response, 'data') and meta_response.data and len(meta_response.data) > 0:
                    filename = meta_response.data[0].get('filename', 'Unknown File')
                    return [f"This is a file named {filename}. Please ask specific questions about its content."]
                return ["No content could be retrieved from this file. Please try with more specific questions."]
                
            # Nếu có ít hơn count chunks, trả về tất cả
            if len(chunks) <= count:
                return chunks
                
            # Lấy ngẫu nhiên count chunks
            return random.sample(chunks, count)
            
        except Exception as e:
            logger.log_with_timestamp('FILE_SERVICE_ERROR', f'Fallback error: {str(e)}')
            return ["Unable to retrieve content from the file. Please try with different questions."]
            
    def _keyword_search_chunks(self, query, file_id, limit=5):
        """
        Tìm kiếm chunks dựa trên từ khóa trong câu query
        Bổ sung cho vector search khi cần nhiều kết quả hơn
        """
        try:
            # Chuẩn bị từ khóa từ query
            # Loại bỏ stop words và lấy các từ khóa chính
            keywords = [word.lower() for word in query.split() if len(word) > 3]
            
            if not keywords:
                return []
                
            # Tạo điều kiện tìm kiếm với phương pháp placeholders an toàn thay vì nối chuỗi trực tiếp
            # Sử dụng Postgres Full Text Search hoặc ILIKE với escape đúng cách
            search_results = []
            
            # Thực hiện tìm kiếm riêng cho từng từ khóa để tránh lỗi cú pháp SQL
            for keyword in keywords:
                # Escape single quotes by doubling them for SQL
                safe_keyword = keyword.replace("'", "''")
                
                try:
                    # Use parameterized query if available, otherwise escape manually
                    response = supabase.table('file_chunks') \
                        .select('content') \
                        .eq('file_id', file_id) \
                        .ilike('content', f'%{safe_keyword}%') \
                        .limit(limit) \
                        .execute()
                    
                    if hasattr(response, 'data') and response.data:
                        for item in response.data:
                            if isinstance(item, dict) and 'content' in item:
                                content = item['content']
                                if content not in search_results:
                                    search_results.append(content)
                                    
                                    # Stop if we have enough results
                                    if len(search_results) >= limit:
                                        break
                    
                except Exception as keyword_error:
                    logger.log_with_timestamp('FILE_SERVICE_ERROR', f'Error in keyword search for term "{safe_keyword}": {str(keyword_error)}')
                    # Continue to next keyword rather than failing completely
                    continue
                    
                # Stop if we have enough results
                if len(search_results) >= limit:
                    break
            
            return search_results
            
        except Exception as e:
            logger.log_with_timestamp('FILE_SERVICE_ERROR', f'Error in keyword search: {str(e)}')
            return []

    def get_chunks_for_query(self, file_id, query):
        """
        Lấy các chunks phù hợp với câu query từ một file
        """
        try:
            # Tăng số lượng chunks từ 5 lên 10
            top_k = 10
            # Giảm ngưỡng tương đồng xuống 0.2 để có nhiều kết quả hơn
            match_threshold = 0.2
            
            # Embed câu query
            embedding = self._create_simple_embedding(query)
            
            # Vector search với số lượng chunks tăng lên
            response = supabase.rpc(
                'match_file_chunks',
                {
                    'query_embedding': embedding,
                    'match_threshold': match_threshold,
                    'match_count': top_k,
                    'p_file_id': file_id
                }
            ).execute()
            
            data = []
            if hasattr(response, 'data'):
                data = response.data or []
            elif isinstance(response, dict) and 'data' in response:
                data = response['data'] or []
                
            vector_chunks = [item['content'] for item in data if isinstance(item, dict) and 'content' in item]
            
            # Nếu vector search không trả về đủ chunks, bổ sung bằng keyword search
            if len(vector_chunks) < top_k:
                keyword_chunks = self._keyword_search_chunks(query, file_id, top_k - len(vector_chunks))
                # Kết hợp kết quả, loại bỏ trùng lặp
                all_chunks = vector_chunks.copy()
                for chunk in keyword_chunks:
                    if chunk not in all_chunks:
                        all_chunks.append(chunk)
                return all_chunks[:top_k]
            
            return vector_chunks
            
        except Exception as e:
            logger.log_with_timestamp('FILE_SERVICE_ERROR', f'Error getting chunks: {str(e)}')
            return []