from flask import Flask, request, jsonify
from flask_cors import CORS
import os, torch, torch.nn.functional as F, torchaudio, requests, tempfile, json
import numpy as np
from inference import load_model, extract_embedding, DEVICE

app = Flask(__name__)
CORS(app)

# ============================================================
# 🔹 Load mô hình
# ============================================================
model = load_model("best_model.pt")
print(f"✅ Model2 đã load thành công trên {DEVICE}")

# ============================================================
# 🔹 API: /predict_embedding
#   → dùng khi đăng ký 3 giọng nói
# ============================================================
@app.route("/predict_embedding", methods=["POST"])
def predict_embedding():
    """
    Nhận nhiều file audio (3 file .wav),
    trích embedding từng file và trả về danh sách embeddings dạng JSON.
    """
    try:
        if "files" not in request.files:
            return jsonify({"error": "Missing audio files"}), 400

        uploaded_files = request.files.getlist("files")
        embeddings = []

        for file in uploaded_files:
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            file.save(tmp.name)
            tmp.close()

            # 🧩 Trích embedding
            emb = extract_embedding(model, tmp.name)

            # Xóa file tạm (nếu được)
            try:
                os.remove(tmp.name)
            except Exception as e:
                print(f"⚠️ Không thể xóa file tạm {tmp.name}: {e}")

            # 🔧 Đảm bảo emb là vector 1-D
            if isinstance(emb, (torch.Tensor, np.ndarray)):
                emb = np.array(emb).reshape(-1)

            embeddings.append(emb.tolist())

        if not embeddings:
            return jsonify({"error": "Không trích được embedding"}), 500

        print(f"✅ Extracted {len(embeddings)} embeddings:")
        for i, e in enumerate(embeddings, 1):
            print(f"   File {i}: {len(e)} dimensions")

        # ✅ Trả về danh sách embedding dạng JSON
        return jsonify({"embeddings": embeddings})

    except Exception as e:
        print("🔥 Lỗi nội bộ Flask:", e)
        return jsonify({"error": str(e)}), 500

# ============================================================
# 🔹 API: /predict
#   → dùng khi xác thực người nói (Django gửi file test + 3 embedding mẫu)
# ============================================================
@app.route("/predict", methods=["POST"])
def predict():
    """
    Nhận 1 file audio test + danh sách 3 embedding mẫu (ref_embeddings),
    trích embedding test và tính cosine similarity.
    """
    try:
        if "audio" not in request.files:
            return jsonify({"error": "No audio file uploaded"}), 400

        # 🟩 Lưu file audio test tạm thời
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        request.files["audio"].save(tmp.name)
        tmp.close()

        # 🟩 Nhận 3 embedding mẫu từ Django
        ref_json = request.form.get("ref_embeddings")
        if not ref_json:
            return jsonify({"error": "Missing reference embeddings"}), 400

        ref_embs = np.array(json.loads(ref_json), dtype=np.float32)  # [3, 192]
        if ref_embs.ndim != 2 or ref_embs.shape[1] != 192:
            return jsonify({"error": f"Invalid ref_embeddings shape: {ref_embs.shape}"}), 400

        # 🟩 Trích embedding test
        test_emb = extract_embedding(model, tmp.name)
        os.remove(tmp.name)

        test_emb = torch.tensor(test_emb, dtype=torch.float32)
        ref_embs = torch.tensor(ref_embs, dtype=torch.float32)

        # 🟩 Trung bình 3 embedding mẫu
        ref_mean = ref_embs.mean(dim=0)

        # 🟩 Tính cosine similarity
        score = float(F.cosine_similarity(test_emb, ref_mean, dim=0).item())
        is_match = score > 0.6

        print(f"✅ Voice verification: score={score:.4f} | match={is_match}")

        return jsonify({
            "score": round(score, 4),
            "is_match": is_match
        })

    except Exception as e:
        print("🔥 Lỗi nội bộ Flask:", e)
        return jsonify({"error": str(e)}), 500

# ============================================================
# 🔹 Main
# ============================================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
