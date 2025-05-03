import asyncio
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from fastapi import Request
from app.database.models import User, Category, Post  # Import your models

# Custom Authentication Backend
class BasicAuthBackend(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")

        # Replace with your admin credentials
        correct_username = "admin"
        correct_password = "password"

        if username == correct_username and password == correct_password:
            request.session.update({"authenticated": True})
            return True

        return False

    async def logout(self, request: Request) -> None:
        request.session.clear()

    async def authenticate(self, request: Request) -> bool:
        return request.session.get("authenticated", False)

# Admin views
class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.username, User.email, User.is_active, User.created_at]
    column_searchable_list = [User.username, User.email]
    column_sortable_list = [User.id, User.created_at]

class CategoryAdmin(ModelView, model=Category):
    column_list = [Category.id, Category.name]

class PostAdmin(ModelView, model=Post):
    column_list = [Post.id, Post.title, Post.description, Post.category_id, Post.author_id]

# Setup SQLAdmin
def setup_admin(app, engine):
    loop = asyncio.get_event_loop()
    admin = Admin(app, engine, authentication_backend=BasicAuthBackend(secret_key="your-secret-key"))
    admin.add_view(UserAdmin)
    admin.add_view(CategoryAdmin)
    admin.add_view(PostAdmin)