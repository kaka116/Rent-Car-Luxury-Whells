from website import create_app

app = create_app()

#run the website
if __name__ == '__main__':
    app.run(debug=True) # Enable debug mode
