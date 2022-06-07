from main import app
import os

if __name__ == "__main__":
    print(os.environ.get("FLASK_APP"))
    app.run(host='0.0.0.0',port=5000)

#test9 CI/CD