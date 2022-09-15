from . import ma

class User_Schema(ma.Schema):
    class Meta:
        fields = (
            'id', 
            'username', 
            'email', 
            'name', 
            "date_of_birth", 
            "is_deleted", 
            "about_user", 
            "sign_up_time"
        )

class Post_Schema(ma.Schema):
    class Meta:
        fields = (
            'id', 
            'post_title', 
            'post_body', 
            'author_id', 
            'date_added', 
            "is_deleted"
        )

class Comment_Schema(ma.Schema):
    class Meta:
        fields = (
            'id', 
            'comment_body', 
            'on_post', 
            'by_user', 
            "time_added", 
            "is_deleted"
        )
        
post_schema = Post_Schema()
posts_schema = Post_Schema(many=True)
user_schema = User_Schema()
users_schema = User_Schema(many=True)
comment_schema = Comment_Schema()
comments_schema = Comment_Schema(many=True)
