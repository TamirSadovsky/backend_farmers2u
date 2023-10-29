from flask import jsonify, request, Blueprint
from app import app
from models import Post, db


deletepost_blueprint = Blueprint('delete_post', __name__)

@app.route('/api/delete_post', methods=['POST'])
def delete_post():
    data = request.form.to_dict()
    post_id = data.get('postId')


    if post_id is None:
        return jsonify({"error": "חלה תקלה, נא לנסות שוב"}), 400
    
    post = Post.query.get(post_id)

    if post is None:
        return jsonify({"error": 'הפוסט לא נמצא'}), 404
    
    try:
        db.session.delete(post)
        db.session.commit()
        return jsonify({"message": "הפוסט נמחק בהצלחה!"}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "הפוסט לא נמחק בהצלחה"}), 500

