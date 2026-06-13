from app import create_app

app = create_app()

if __name__ == "__main__":
    print(">>> Iniciando Sistema Safira MusiCloud...")
    app.run(debug=True)
