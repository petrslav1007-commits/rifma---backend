import pymorphy3
import requests

from flask import Flask, request, jsonify
from flask_cors import CORS
from wordfreq import zipf_frequency


app = Flask(__name__)
CORS(app)

morph = pymorphy3.MorphAnalyzer()

RHYME_BRAIN_URL = "https://rhymebrain.com/talk"


@app.route("/rhymes", methods=["GET"])
def rhymes():

    word = request.args.get(
        "word",
        ""
    ).strip().lower()

    if not word:
        return jsonify({
            "error": "word is required"
        }), 400

    try:

        response = requests.get(
            RHYME_BRAIN_URL,
            params={
                "function": "getRhymes",
                "word": word,
                "lang": "ru",
                "maxResults": 100
            },
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

    except Exception as error:

        print(
            "RhymeBrain error:",
            error
        )

        return jsonify({
            "error": "failed to get rhymes"
        }), 500


    result = []
    seen = set()


    for item in data:

        candidate = (
            item.get("word", "")
            .strip()
            .lower()
        )

        if not candidate:
            continue

        if candidate == word:
            continue

        if candidate in seen:
            continue

        seen.add(candidate)


        # Проверяем, что слово существует
        parses = morph.parse(candidate)

        if not parses:
            continue


        best = max(
            parses,
            key=lambda p: p.score
        )


        # Отбрасываем совсем слабые разборы
        if best.score < 0.3:
            continue


        # Проверяем частотность русского слова
        frequency = zipf_frequency(
            candidate,
            "ru"
        )

        # Отсекаем откровенный мусор
        if frequency < 3.0:
            continue


        result.append({
            "word": candidate,
            "score": item.get(
                "score",
                0
            ),
            "frequency": frequency,
            "morph_score": best.score,
            "pos": best.tag.POS
        })


    # Сначала качество рифмы,
    # затем частотность слова
    result.sort(
        key=lambda item: (
            item["score"],
            item["frequency"]
        ),
        reverse=True
    )


    return jsonify(result)


@app.route("/analyze", methods=["GET"])
def analyze():

    word = request.args.get(
        "word",
        ""
    ).strip().lower()

    if not word:
        return jsonify({
            "error": "word is required"
        }), 400


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

    app.run(
        host="0.0.0.0",
        port=10000
    )
