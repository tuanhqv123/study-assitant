from app import create_app, logger

if __name__ == '__main__':
    start_message = f"===== Study Assistant API started at {logger.get_timestamp()} ====="
    print("=" * len(start_message))
    print(start_message)
    print("=" * len(start_message))
    
    app = create_app()
    app.run(port=5000, debug=True)