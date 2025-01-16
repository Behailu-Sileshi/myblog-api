import pytest
from rest_framework import status


POST_BASE_URL = '/blog/posts/'

@pytest.fixture
def create_post(api_client):
    def do_create_post(data):
        return api_client.post(POST_BASE_URL, data)
    return do_create_post

@pytest.fixture
def retrieve_post(api_client):
    def do_retrieve_post(id):
        return api_client.get(f"{POST_BASE_URL}{id}/")
    return do_retrieve_post

@pytest.fixture
def update_post(api_client):
    def do_update_post(id, data):
        return api_client.put(f"{POST_BASE_URL}{id}/", data)
    return do_update_post

@pytest.fixture
def delete_post(api_client):
    def do_delete_post(id):
        return api_client.delete(f"{POST_BASE_URL}{id}/")
    return do_delete_post


@pytest.mark.django_db
class TestPostCreation:
    def test_anonymous_user_cannot_create_post(self, create_post):
        response = create_post({'title': 'a'})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_invalid_data_returns_400(self, authenticate, create_post):
        authenticate()
        response = create_post({'title': ''})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_valid_data_creates_post(self, authenticate, create_post):
        authenticate()
        data = {'title': 'Valid Post', 'body': 'This is a valid post.'}
        response = create_post(data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == 'Valid Post'

@pytest.mark.django_db
class TestPostRetrieval:
    def test_nonexistent_post_returns_404(self, retrieve_post):
        response = retrieve_post(999)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_existing_post_returns_200(self, create_post_instance, retrieve_post):
        post = create_post_instance(title='Test Post')
        response = retrieve_post(post.id)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == post.id

@pytest.mark.django_db
class TestPostUpdate:
    def test_anonymous_user_cannot_update_post_returns_401(self, update_post):
        response = update_post(1, {'title': 'Updated Title'})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_nonexistent_post_returns_404(self, authenticate, update_post):
        authenticate()
        response = update_post(999, {'title': 'Updated Title'})
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_invalid_data_returns_400(self, create_post_instance, update_post):
        post = create_post_instance()
        response = update_post(post.id, {'title': ''})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_non_owner_cannot_update_post_returns_403(self, create_post_instance, authenticate, update_post):
        post = create_post_instance()
        authenticate()
        response = update_post(post.id, {'title': 'Updated Title'})
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_valid_data_updates_post_returns_200(self, create_post_instance, update_post):
        post = create_post_instance()
        data = {'title': 'Updated Title', 'body': post.body}
        response = update_post(post.id, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'Updated Title'

@pytest.mark.django_db
class TestPostDeletion:
    def test_anonymous_user_cannot_delete_post(self, delete_post):
        response = delete_post(1)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_nonexistent_post_returns_404(self, authenticate, delete_post):
        authenticate()
        response = delete_post(999)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_non_owner_cannot_delete_post_return_403(self, create_post_instance, authenticate, delete_post):
        post = create_post_instance()
        authenticate()
        response = delete_post(post.id)
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_owner_can_delete_post_returns_204(self, create_post_instance, delete_post):
        post = create_post_instance()
        response = delete_post(post.id)
        assert response.status_code == status.HTTP_204_NO_CONTENT
