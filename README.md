# Blog API

## Project Overview
The Blog API is designed to manage blog posts, authors, comments, and multimedia content such as images and videos. This API allows users to create, retrieve, update, and delete blog posts while handling associated comments and media.

## Features
- User Authentication
- User Profile
- CRUD operations for Blog Posts
- Nested Comments for Posts
- Multimedia (Images & Videos) Management for posts
- Follow/Unfollow functionality for Authors

## Technologies Used
- Django
- Django REST Framework
- MySql
- pytest for testing

## Installation

1. **Clone the Repository:**
   ```bash
   git clone <repository-url>
   cd blog-api
   ```

2. **Set up a Virtual Environment:**
   ```bash
   pipenv shell 
   ```

3. **Install Dependencies:**
   ```bash
   pipenv install
   ```

4. **Apply Migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Run the Development Server:**
   ```bash
   python manage.py runserver
   ```

## API Endpoints

### Authentication
- **POST** `/auth/jwt/create` - Obtain a new token.
- **POST** `/auth/jwt/refresh/` - Refresh an existing token.

### Authors
- **GET** `/authors/` - Retrieve a list of authors.
- **GET** `/authors/me` - Retrieve author profile.
- **PUT** `/authors/me` - Retrieve author profile.
- **GET** `/authors/{id}/` - Retrieve a specific author.

### Posts
- **GET** `/posts/` - Retrieve a list of posts.
- **POST** `/posts/` - Create a new post.
- **GET** `/posts/{id}/` - Retrieve a specific post.
- **PUT** `/posts/{id}/` - Update a specific post.
- **DELETE** `/posts/{id}/` - Delete a specific post.

### Comments
- **GET** `/posts/{post_id}/comments/` - Retrieve comments for a specific post.
- **POST** `/posts/{post_id}/comments/` - Add a comment to a specific post.
- **GET** `/posts/{post_id}/comments/{id}/` - Add a comment to a specific post.

### Media
- **POST** `/posts/{post_id}/images/` - Upload an image for a specific post.
- **POST** `/posts/{post_id}/videos/` - Upload a video for a specific post.

### Follow/Unfollow
- **POST** `/follow/{author_id}/` - Follow a specific author.
- **DELETE** `/unfollow/{author_id}/` - Unfollow a specific author.
- **GET** `/followers/` - List followers of the authenticated user.
- **GET** `/followings/` - List authors followed by the authenticated user.

## Testing

Run tests using `pytest`:

```bash
pytest
```

### Fixtures
- **`api_client`**: Provides an instance of `APIClient` for making test requests.
- **`authenticate`**: Authenticates a user for testing.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Contribution
Feel free to fork the repository and submit pull requests. For major changes, please open an issue first to discuss what you would like to change.

## Acknowledgments
 - Django and Django REST Framework documentation


## Contact
For any inquiries or issues, please contact [behailusileshi7@gmail.com].

