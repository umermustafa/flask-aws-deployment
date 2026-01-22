from flask import Flask, jsonify, request
from flask_caching import Cache
import time
import random
import logging
import os
from flask_compress import Compress
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
app.config.from_object("config.Config")
Compress(app)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)

cache = Cache(app)

logging.basicConfig(level=logging.INFO)

@app.route("/")
def home():
    app.logger.info("Home endpoint hit")
    return jsonify(message="Hello from Flask v2 deployed via ci-cd pipeline")

@app.route("/health")
def health():
    return jsonify(status="OK"), 200

@app.route("/heavy")
def heavy():
    app.logger.info("Heavy endpoint simulating load")
    time.sleep(65)  # Simulate a heavy computation or DB call
    return jsonify(result="Heavy computation done!")

@app.route("/cacheme/<param>")
@cache.cached(timeout=120)
def cacheme(param):
    time.sleep(20)
    worker = os.getpid()
    app.logger.info(f"Caching result for: {param} (worker {worker})")
    return jsonify(
        result=f"Processed {param}",
        random=random.randint(1, 1000),
        worker=worker
    )

@app.route("/bigjson")
def bigjson():
    # Simulate a large JSON (e.g., 2000 items)
    data = [{"item": i, "value": "x" * 100} for i in range(2000)]
    return jsonify(data)

@app.route('/api')
@limiter.limit("5/minute")
def api():
    worker = os.getpid()
    app.logger.info(f"limiter (worker {worker})")
    return "success"

@app.route("/error")
def error():
    app.logger.error("Intentional error triggered")
    raise Exception("This is a test error for monitoring/logging purposes")

# Error handler
@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.exception("Unhandled exception occurred")
    return jsonify(error=str(e)), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
