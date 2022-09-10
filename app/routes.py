from re import A
from flask import Flask, request, jsonify, Response
from app import app, db
from app import schemas
from typing import Any
from app.models import User, Posts, Comments

get_only = ["GET"]
post_only = ["POST"]
both_ = ["GET", "POST"]

@app.route('/')
def base() -> Response:
    return Response("Server Running")

@app.route('/login')
def login() -> str:
    """Checks Login Information with the db
    Format
    data = {"username": str -> username, "password": str -> password}

    Returns:
        str: data in response['data'], keys are ['login', 'user_id'] OR ['login', 'error']
    """
    data = request.get_json()
    if request.method == "POST" and data:
        username = data["username"]
        password = data["password"]
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            return jsonify(good_response({"login": True, "user_id": user.id, "token": user.get_token()}))
        else:
            return jsonify(bad_response({"login": False, "error": "User doesn't Exist"}))
    else:
        return jsonify(good_response({"login": False, "error": "bad request"}))

@app.route('/users', methods=['GET'])
def users() -> str:
    """Gets All Users

    Returns:
        str: data in response['data'], List[Dict[str, Any]]
    """
    all_users = User.query.all()
    result = schemas.users_schema.dump(all_users)
    return jsonify(good_response(result))

@app.route('/add_user', methods=both_)
def add_user() -> str:
    """Adds a User
    Format:
    data = {"username": str -> username, "password": str -> password, "name": str -> name, "date_of_birth": str -> dob <"DD-MM-YYYY">}

    Returns:
        str: data in response['data'], keys are ['user_id'] OR ['error']
    """
    data = request.get_json()
    if data and request.method == "POST":
        user = User.query.filter_by(username=data['username']).first()
        if user and not user.is_deleted:
            return jsonify(bad_response(({'error': "User Already Exists"})))
        new_user = User(
            username=data["username"],
            password=data["password"],
            name=data["name"],
            date_of_birth=data["date_of_birth"],
            is_deleted=False,
        )
        new_user.set_token()
        add(new_user)
        return jsonify(good_response({"user_id": new_user.user_id, "user_token": new_user.get_token()}))
    else:
        return jsonify(good_response({"error": "bad request"}))

@app.route('/user/<user_id>/about/add_about', methods=both_)
def add_about(user_id: int) -> str:
    """Format
    data = {"about": str -> about, "token": str -> token}

    Args:
        user_id (int): user_id to Change About in

    Returns:
        str: json data in ["data"]
    """
    user = User.query.get(user_id)
    data = request.get_json()["about"]
    if user and data and user.token == data["token"]:
        user.set_about_user(data["about"])
        return jsonify(good_response(f"about added for user {user.username}"))
    else:
        return jsonify(bad_response({"error": "couldn't add About"}))

@app.route('/user/<user_id>/about', methods=both_)
def about(user_id: int) -> str:
    """User About

    Args:
        user_id (int): user_id

    Returns:
        str: data in response['data'], keys are ['username', 'password', 'name', 'posts', 'len_posts', 'comments', 'user_id', 'age']
    """

    user = User.query.get(user_id)
    result = schemas.user_schema.dump(user)
    result['posts'] = schemas.posts_schema.dump(user.posts.all())
    all_comments = user.comments_by_user.all()
    result['comments'] = schemas.comments_schema.dump(all_comments)
    for i in range(len(result["posts"])):
        result["posts"][i]["by_user"] = user.username
    for i in range(len(result["comments"])):
        result["comments"][i]["on_post"] = all_comments[i].comment_post.post_title
        result["comments"][i]["post_by"] = all_comments[i].comment_post.writer.username
    result['len_posts'] = len(result['posts'])
    return jsonify(good_response(result))

@app.route('/user/<user_id>/delete', methods=both_)
def delete_user(user_id: int) -> str:
    """Delete A User
    Format
    data = {"token": user_token}

    Args:
        user_id (int): user_id to Delete User

    Returns:
        str: data in response['data'], keys are ['result']
    """

    user = User.query.get(user_id)
    if user and user.get_token() == request.get_json()["token"]:
        user.delete_user()
        db.session.commit()
        return jsonify(good_response({"result": 'User Deleted'}))
    else:
        return jsonify(bad_response(result={"error": "token bad"}))

@app.route('/user/<user_id>/add_post', methods=['GET', 'POST'])
def add_post(user_id: int) -> str:
    """Adds a Post
    Format:
    data = {"post_title": str -> post_title, "post_body": str -> post_body, "token": str -> user_token}

    Returns:
        str: data in response['data'], keys are ['post_id'] OR ['error']
    """
    data = request.get_json()
    if request.method == "POST" and data:
        user = User.query.get(user_id)
        if user and user.get_token() == data["token"]:
            post = Posts(
                post_title=data['post_title'],
                post_body=data["post_body"],
                writer=user,
            )
            add(post)
            return jsonify(good_response({"post_id": post.post_id}))
    else:
        return jsonify(bad_response({"error": "bad request"}))

@app.route('/user/<user_id>/view_post/<post_id>', methods=['GET', 'POST'])
def view_post(user_id: int, post_id: int) -> str:
    """Views a Post

    Args:
        user_id (int): user_id
        post_id (int): post_id

    Returns:
        str: data in response['data'], keys are ['post_title', 'post_id', 'post_body', 'user']
    """    
    post_id = post_id
    post = Posts.query.get(post_id)
    if not post.is_deleted:
        result = schemas.post_schema.dump(post)
        result['by_user'] = post.writer.username
        all_comments = post.comments.all()
        result['comments'] = schemas.comments_schema.dump(all_comments)
        for i in range(len(result['comments'])):
            result["comments"][i]['by_user'] = all_comments[i].comment_by_user.username
            result["comments"][i]["user_id"] = all_comments[i].comment_by_user.user_id
        return jsonify(good_response(result))
    else:
        return jsonify(bad_response("[post_deleted]"))
    

@app.route('/user/post/add_comment', methods=["GET", "POST"])
def add_comment() -> str:
    """Adds a Comment
    Format:
    data = {"user_id": int -> user_id, "post_id": int -> post_id, "comment_body": str -> comment_body, "token": str-> user_token}

    Returns:
        str: data in response['data'], keys are ['comment_id', 'post_id'] OR ['error']
    """    
    data = request.get_json()
    if request.method == "POST" and data:
        user = User.query.get(data["user_id"])
        if user.get_token() == data['token']:
            if not Posts.query.get(data["post_id"]).first().is_deleted:
                comment = Comments(
                    comment_body=data["comment_body"],
                    comment_by_user=user,
                    comment_post=Posts.query.get(data["post_id"]),
                )
                add(comment)
                return jsonify(good_response({"comment_id": comment.comment_id, "post_id": data["post_id"]}))

@app.route('/user/post/<post_id>/delete', methods=['GET', 'POST'])
def delete_post(post_id: int) -> str:
    """Delete a Post
    format:
    Data = {"user_id": int -> user_id, "token": str-> user_token}

    Args:
        post_id (int): post_id to delete

    Returns:
        str: data in response['data'], keys are ['result']
    """
    data = request.get_json()
    user = User.query.get(data["user_id"])
    if user and user.get_token() == data["token"]:
        post = Posts.query.get(post_id)
        post.delete_post()
        db.session.commit()
        return jsonify(good_response({"result": "Post Deleted"}))

@app.route('/user/comment/<comment_id>/delete', methods=['GET',"POST"])
def delete_comment(comment_id: int) -> str:
    """Deletes a User Comment

    Returns:
        str: data in response['data'], keys are ['result']
    """
    data = request.get_json()
    user = User.query.get(data["user_id"])
    if user and user.get_token() == data["token"]:
        comment = Comments.query.get(comment_id)
        comment.delete_comment()
        db.session.commit()
        return jsonify(good_response({"result": "Post Deleted"}))

# OTHER Methods
def delete(object):
    db.session.delete(object)
    db.session.commit()
def add(object):
    db.session.add(object)
    db.session.commit()
def good_response(data: Any):
    return {'response': "good", 'data': data}
def bad_response(data: Any):
    return {'response': "bad", 'data': data}
