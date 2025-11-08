from flask import Flask, request, jsonify
from flask_cors import CORS
import os, torch, torch.nn.functional as F, torchaudio, requests, tempfile, json, subprocess
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
# 🔹 Hàm hỗ trợ: lưu & convert audio về chuẩn WAV 16kHz mono
# ============================================================
def save_and_normalize_to_wav(file_storage, target_sr=16000):
    """
    Lưu file upload ra tệp tạm.
    Nếu không đọc được bằng torchaudio (không phải WAV hợp lệ),
    chuyển đổi bằng ffmpeg sang WAV mono 16kHz rồi trả về đường dẫn file WAV cuối cùng.
    """
    # 1️⃣ Lưu file upload tạm
    tmp_in = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    file_storage.save(tmp_in.name)
    tmp_in.close()

    # 2️⃣ Kiểm tra format
    try:
        torchaudio.info(tmp_in.name)
        return tmp_in.name  # file hợp lệ, trả luôn
    except Exception as e:
        print(f"⚠️ Không đọc được trực tiếp bằng torchaudio: {e}")

    # 3️⃣ Convert bằng ffmpeg
    tmp_out = tmp_in.name.replace(".wav", "_fixed.wav")
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", tmp_in.name, "-ar", str(target_sr), "-ac", "1", tmp_out],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        torchaudio.info(tmp_out)  # xác nhận hợp lệ
        os.remove(tmp_in.name)
        print(f"🔄 Đã convert {tmp_in.name} → {tmp_out}")
        return tmp_out
    except Exception as e2:
        print(f"🔥 Không thể convert bằng ffmpeg: {e2}")
        return tmp_in.name  # fallback


# ============================================================
# 🔹 API: /predict_embedding
#   → dùng khi đăng ký 3 giọng nói
# ============================================================
@app.route("/predict_embedding", methods=["POST"])
def predict_embedding():
    """
    Nhận nhiều file audio (3 file .wav, .webm, .m4a,...),
    trích embedding từng file và trả về danh sách embeddings dạng JSON.
    """
    try:
        if "files" not in request.files:
            return jsonify({"error": "Missing audio files"}), 400

        uploaded_files = request.files.getlist("files")
        embeddings = []

        for file in uploaded_files:
            # ✅ Chuẩn hóa audio trước khi xử lý
            wav_path = save_and_normalize_to_wav(file)

            emb = extract_embedding(model, wav_path)

            try:
                os.remove(wav_path)
            except Exception as e:
                print(f"⚠️ Không thể xóa file tạm {wav_path}: {e}")

            # 🔧 Đảm bảo emb là vector 1-D
            if isinstance(emb, (torch.Tensor, np.ndarray)):
                emb = np.array(emb).reshape(-1)

            embeddings.append(emb.tolist())

        if not embeddings:
            return jsonify({"error": "Không trích được embedding"}), 500

        print(f"✅ Extracted {len(embeddings)} embeddings:")
        for i, e in enumerate(embeddings, 1):
            print(f"   File {i}: {len(e)} dimensions")

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

        ref_json = request.form.get("ref_embeddings")
        if not ref_json:
            return jsonify({"error": "Missing reference embeddings"}), 400

        ref_embs = np.array(json.loads(ref_json), dtype=np.float32)  # [3, 192]
        if ref_embs.ndim != 2 or ref_embs.shape[1] != 192:
            return jsonify({"error": f"Invalid ref_embeddings shape: {ref_embs.shape}"}), 400

        # ✅ Chuẩn hóa file test audio
        wav_path = save_and_normalize_to_wav(request.files["audio"])

        test_emb = extract_embedding(model, wav_path)
        try:
            os.remove(wav_path)
        except:
            pass

        test_emb = torch.tensor(test_emb, dtype=torch.float32)
        ref_embs = torch.tensor(ref_embs, dtype=torch.float32)
        ref_mean = ref_embs.mean(dim=0)

        score = float(F.cosine_similarity(test_emb, ref_mean, dim=0).item())
        is_match = score > 0.6

        print(f"✅ Voice verification: score={score:.4f} | match={is_match}")

        return jsonify({"score": round(score, 4), "is_match": is_match})

    except Exception as e:
        print("🔥 Lỗi nội bộ Flask:", e)
        return jsonify({"error": str(e)}), 500


# ============================================================
# 🔹 Main
# ============================================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
