from flask import Flask, request, jsonify
import single_access_kpi, fmea, all_access_kpi,health_index

app = Flask(__name__)

@app.route("/single_access_kpi", methods=["POST"])

def handle_single_access_kpi():
    return process_request(single_access_kpi.main)

@app.route("/fmea", methods=["POST"])

def handle_fmea():
    return process_request(fmea.main)

@app.route("/all_access_kpi", methods=["POST"])

def handle_all_access_kpi():
    return process_request(all_access_kpi.main)

@app.route("/health_index", methods=["POST"])

def handle_health_index():
    return process_request(health_index.main)

def process_request(function_to_call):
    try:
        incoming_data = request.get_json(force=True, silent=True)
        #print(incoming_data)

        if not incoming_data or not isinstance(incoming_data, dict):
            return jsonify({"result": "", "error": "Invalid or missing JSON data"}), 400

        args = {"body": incoming_data}
        processed_data = function_to_call(args, {})
        return jsonify({"result": processed_data, "error": ""}), 200

    except Exception as e:
        return jsonify({
            "result": "",
            "error": str(e) or "An unexpected error occurred."
        }), 500

@app.after_request
def add_header(response):
    response.cache_control.no_store = True
    response.cache_control.must_revalidate = True
    return response

if __name__ == "__main__":
    app.run(debug=True, port=5005)
