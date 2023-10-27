from flask import Flask, request

app = Flask(__name__)

@app.route('/alert', methods=['POST'])
def receive_post_request():
    if request.method == 'POST':
        # Get the request body (data)
        print(request)
        request_data =request.form.to_dict()
        
        # Print the request body
        print("Received POST request with data:")
        print(request_data)

        # You can process the request data further here if needed
        return 'POST request received'

if __name__ == '__main__':
    app.run(debug=True)
