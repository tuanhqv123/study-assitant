from flask import Blueprint, request, jsonify
from ..services.file_service import FileService
from ..utils.logger import Logger
import traceback

file_bp = Blueprint('file', __name__)
logger = Logger()
service = FileService()

@file_bp.route('/upload', methods=['POST'])
def upload_file():
    logger.log_with_timestamp('FILE_UPLOAD', 'Bắt đầu xử lý request upload file')
    
    # Log request details
    logger.log_with_timestamp('FILE_UPLOAD', f'Request form data: {list(request.form.keys())}')
    logger.log_with_timestamp('FILE_UPLOAD', f'Request files: {list(request.files.keys()) if request.files else "No files"}')
    
    # Expect multipart/form-data with 'file' and 'user_id'
    user_id = request.form.get('user_id')
    if not user_id:
        logger.log_with_timestamp('FILE_UPLOAD_ERROR', 'Missing user_id in request form data')
        return jsonify({'error': 'Missing user_id'}), 400

    logger.log_with_timestamp('FILE_UPLOAD', f'User ID: {user_id}')

    if 'file' not in request.files:
        logger.log_with_timestamp('FILE_UPLOAD_ERROR', 'No file found in request files')
        return jsonify({'error': 'No file provided'}), 400
        
    file = request.files['file']
    if file.filename == '':
        logger.log_with_timestamp('FILE_UPLOAD_ERROR', 'Empty filename')
        return jsonify({'error': 'Empty filename'}), 400
        
    logger.log_with_timestamp('FILE_UPLOAD', f'File received: {file.filename}, Content-Type: {file.content_type}, Size: {file.content_length or "unknown"} bytes')

    try:
        # extract text content (assume text extraction earlier done by caller)
        from ..services.file_service import FileService
        
        # PDF files should be processed differently than text files
        if file.content_type == 'application/pdf':
            try:
                logger.log_with_timestamp('FILE_UPLOAD', 'Processing PDF file...')
                # For PDF files, we need to use a PDF parser
                import PyPDF2
                import io
                
                # Create a file-like object from the uploaded file
                pdf_file = io.BytesIO(file.read())
                
                # Create PDF reader
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                
                # Extract text from all pages
                text_content = ""
                for page in pdf_reader.pages:
                    text_content += page.extract_text() + "\n"
                    
                logger.log_with_timestamp('FILE_UPLOAD', f'Successfully extracted {len(text_content)} characters from PDF')
                content = text_content
            except ImportError:
                logger.log_with_timestamp('FILE_UPLOAD_ERROR', 'PyPDF2 library not installed, trying fallback method')
                # Fallback to binary read if PyPDF2 is not available
                file.seek(0)  # Reset file pointer to beginning
                content = file.read().decode('utf-8', errors='ignore')
        else:
            # For text files, just read as text
            content = file.read().decode('utf-8', errors='ignore')
            logger.log_with_timestamp('FILE_UPLOAD', f'Extracted {len(content)} characters from text file')
        
        # Log content sample for debugging
        content_sample = content[:200] + "..." if len(content) > 200 else content
        logger.log_with_timestamp('FILE_UPLOAD', f'Content sample: {content_sample}')
        
        # Reset file pointer for FileService
        file.seek(0)
        
        # process and save - Đã chuyển về gọi hàm đồng bộ
        logger.log_with_timestamp('FILE_UPLOAD', 'Saving to Supabase...')
        file_id = service.save_file_and_chunks_to_supabase(user_id, file, content)
        logger.log_with_timestamp('FILE_UPLOAD', f'Successfully saved file with ID: {file_id}')
        return jsonify({'success': True, 'file_id': file_id, 'filename': file.filename})
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.log_with_timestamp('FILE_UPLOAD_ERROR', f'Error: {str(e)}\nTraceback: {error_trace}')
        return jsonify({'error': str(e)}), 500

@file_bp.route('/list', methods=['GET'])
def list_files():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'Missing user_id'}), 400
    try:
        res = service.supabase.table('user_files').select('id, filename, created_at').eq('user_id', user_id).order('created_at', desc=True).execute()
        data = res.data or []
        return jsonify({'files': data})
    except Exception as e:
        logger.log_with_timestamp('FILE_ROUTE_ERROR', str(e))
        return jsonify({'error': str(e)}), 500

@file_bp.route('/<uuid:file_id>', methods=['DELETE'])
def delete_file(file_id):
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'Missing user_id'}), 400
    try:
        # delete metadata (cascade deletes chunks)
        res = service.supabase.table('user_files').delete().eq('id', str(file_id)).eq('user_id', user_id).execute()
        if res.error:
            raise Exception(res.error.message)
        return jsonify({'success': True})
    except Exception as e:
        logger.log_with_timestamp('FILE_ROUTE_ERROR', str(e))
        return jsonify({'error': str(e)}), 500