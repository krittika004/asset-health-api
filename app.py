from app.factory import create_app

if __name__ == '__main__':
    app = create_app()
    print("Your app is live at: http://127.0.0.1:5000 (CTRL+C to stop)")
    app.run(
        debug=True,
        host='127.0.0.1',
        port=5000,
        use_reloader=True
    )
