import pytest
from rest_framework import status
from blog.models import Comment
from model_bakery import baker

POST_BASE_URL = '/blog/posts/'

@pytest.fixture
def create_comment(api_client):
    def do_create_comment(post_id, data):
        return api_client.post(f"{POST_BASE_URL}{post_id}/comments/", data)
    return do_create_comment

@pytest.fixture
def retrieve_comment(api_client):
    def do_retrieve_comment(post_id, comment_id):
        return api_client.get(f"{POST_BASE_URL}{post_id}/comments/{comment_id}/")
    return do_retrieve_comment

@pytest.fixture
def update_comment(api_client):
    def do_update_comment(post_id, comment_id, data):
        return api_client.put(f"{POST_BASE_URL}{post_id}/comments/{comment_id}/", data)
    return do_update_comment

@pytest.fixture
def delete_comment(api_client):
    def do_delete_comment(post_id, comment_id):
        return api_client.delete(f"{POST_BASE_URL}{post_id}/comments/{comment_id}/")
    return do_delete_comment

@pytest.fixture
def create_comment_instance(authenticate, create_post_instance):
    def do_create_comment_instance(**kwargs):
        post = create_post_instance()
        user = authenticate()
        return baker.make(Comment, post_id=post.id, owner=user.author, **kwargs)
    return do_create_comment_instance

@pytest.mark.django_db
class TestCommentCreation:
    def test_anonymous_user_cannot_create_comment(self, api_client, create_post_instance, create_comment):
        post = create_post_instance()
        api_client.logout()
        
        response = create_comment(post.id, {"body": "test"})
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_invalid_data_returns_400(self, authenticate, create_post_instance, create_comment):
        post = create_post_instance()
        authenticate()
        
        response = create_comment(post.id, {'body': ''})
       
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
    def test_valid_data_creates_comment(self, authenticate, create_post_instance, create_comment):
        post = create_post_instance()
        authenticate()
        
        response = create_comment(post.id, {'body': 'test'})
       
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['body'] == 'test'

@pytest.mark.django_db
class TestCommentRetrieval:
    def test_nonexistent_comment_returns_404(self, create_post_instance, retrieve_comment):
        post = create_post_instance()
        
        response = retrieve_comment(post.id, 999)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_existing_comment_returns_200(self, create_comment_instance, retrieve_comment):
        comment = create_comment_instance()
        
        response = retrieve_comment(comment.post.id, comment.id)
        
        assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
class TestCommentUpdate:
    def test_anonymous_user_cannot_update_comment(self, api_client, create_comment_instance, update_comment):
        comment = create_comment_instance()
        api_client.logout()
        
        response = update_comment(comment.post.id, comment.id, {'body': 'updated'})
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_nonexistent_comment_returns_404(self, create_post_instance, update_comment):
        post = create_post_instance()
        
        response = update_comment(post.id, 999, {'body': "update"})
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_user_not_owner_cannot_update_comment(self, authenticate, create_comment_instance, update_comment):
        comment = create_comment_instance()
        authenticate()
        
        response = update_comment(comment.post.id, comment.id, {'body': 'update'})
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_invalid_data_returns_400(self, create_comment_instance, update_comment):
        comment = create_comment_instance()
        
        response = update_comment(comment.post.id, comment.id, {'body': ''})
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
    def test_valid_data_updates_comment(self, create_comment_instance, update_comment):
        comment = create_comment_instance()
        
        response = update_comment(comment.post.id, comment.id, {'body': 'updated'})
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['body'] == 'updated'
        
@pytest.mark.django_db
class TestCommentDeletion:
    def test_anonymous_user_cannot_delete_comment(self, api_client, create_comment_instance, delete_comment):
        comment = create_comment_instance()
        api_client.logout()
        
        response = delete_comment(comment.post.id, comment.id)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
    def test_nonexistent_comment_returns_404(self, create_post_instance, delete_comment):
        post = create_post_instance()
        
        response = delete_comment(post.id, 999)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_user_not_owner_cannot_delete_comment(self, authenticate, create_comment_instance, delete_comment):
        comment = create_comment_instance()
        authenticate()
        
        response = delete_comment(comment.post.id, comment.id)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
    def test_owner_can_delete_comment(self, create_comment_instance, delete_comment):
        comment = create_comment_instance()
        
        response = delete_comment(comment.post.id, comment.id)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
