from app import app

def run():
  app.run(host='0.0.0.0',port=583)
  app.run(debug=True)

def keep_alive():
    t = Thread(target=run)
    t.start()
    
keep_alive()