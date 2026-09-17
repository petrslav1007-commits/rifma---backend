from flask import Flask, request, jsonify
from flask_cors import CORS
import pymorphy3

app = Flask(__name__)
CORS(app)

morph = pymorphy3.MorphAnalyzer()


@app.route("/analyze", methods=["GET"])
def analyze():
    word = request.args.get("word", "").strip().lower()

    if not word:
        return jsonify({"error": "word is required"}), 400

    parses = morph.parse(word)

    result = []

    for p in parses:
        result.append({
            "word": word,
            "pos": p.tag.POS,
            "score": p.score
        })

    return jsonify(result)


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "ok",
        "service": "РИФМА morphology"
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
