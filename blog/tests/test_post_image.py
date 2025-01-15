import pytest
from rest_framework import status
from model_bakery import baker
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import io
from blog.models import PostImage


BASE_POST_URL = '/blog/posts/'

# Fixtures
@pytest.fixture
def create_post_image(api_client):
    def do_create_post_image(post_id, data):
        return api_client.post(f"{BASE_POST_URL}{post_id}/images/", data, format='multipart')
    return do_create_post_image

@pytest.fixture
def retrieve_post_image(api_client):
    def do_retrieve_post_image(post_id, image_id):
        return api_client.get(f"{BASE_POST_URL}{post_id}/images/{image_id}/")
    return do_retrieve_post_image

@pytest.fixture
def update_post_image(api_client):
    def do_update_post_image(post_id, image_id, data):
        return api_client.put(f"{BASE_POST_URL}{post_id}/images/{image_id}/", data, format='multipart')
    return do_update_post_image
@pytest.fixture
def delete_post_image(api_client):
    def do_delete_post_image(post_id, image_id):
        return api_client.delete(f"{BASE_POST_URL}{post_id}/images/{image_id}/")
    return do_delete_post_image



@pytest.fixture
def create_upload_file():
    def do_create_upload_file():
        image = Image.new('RGB', (100, 100), color='red')
        image_file = io.BytesIO()
        image.save(image_file, format='JPEG')
        image_file.seek(0)
        uploaded_image = SimpleUploadedFile(
            "test_image.jpg",
            image_file.read(),
            content_type="image/jpeg"
        )
        return uploaded_image
    return do_create_upload_file

@pytest.fixture
def create_post_image_instance(create_upload_file, create_post_instance):
    def do_create_post_image_instance():
        post = create_post_instance()
        image = create_upload_file()
        return baker.make(PostImage, post_id=post.id, image=image)
    return do_create_post_image_instance

# Test Classes
@pytest.mark.django_db
class TestPostImageCreation:
    
    def test_anonymous_user_cannot_upload(self, api_client, create_post_instance, create_post_image, create_upload_file):
        post = create_post_instance()
        api_client.logout()
        upload_image = create_upload_file()
        response = create_post_image(post.id, {"image": upload_image})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_user_not_owner_cannot_upload(self, authenticate, create_post_instance, create_post_image, create_upload_file):
        post = create_post_instance()
        authenticate()
        upload_image = create_upload_file()
        response = create_post_image(post.id, {"image": upload_image})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_invalid_data_returns_400(self, create_post_instance, create_post_image):
        post = create_post_instance()
        response = create_post_image(post.id, {"image": 'x'})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_valid_data_creates_image(self, authenticate, create_post_instance, create_post_image, create_upload_file):
        post = create_post_instance()
        upload_image = create_upload_file()
        response = create_post_image(post.id, {"image": upload_image})
        assert response.status_code == status.HTTP_201_CREATED
        assert 'id' in response.data and response.data['id'] > 0
@pytest.mark.django_db
class TestPostImageRetrieval:

    def test_image_not_found(self, create_post_instance, retrieve_post_image):
        post = create_post_instance()
        response = retrieve_post_image(post.id, 999)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_image_found_returns_200(self, create_post_image_instance, retrieve_post_image):
        image = create_post_image_instance()
        response = retrieve_post_image(image.post_id, image.id)
        assert response.status_code == status.HTTP_200_OK
@pytest.mark.django_db
class TestPostImageUpdate:
    def test_image_not_found(self, create_post_instance, update_post_image):
        post = create_post_instance()
        response = update_post_image(post.id, 999, {})
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
    def test_user_is_not_owner_returns_403(self, authenticate, create_post_image_instance, update_post_image):
        image = create_post_image_instance()
        authenticate()
        response = update_post_image(image.post_id, image.id, {'image': image.image, 'caption': 'hello'})
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
    def test_invalid_data_returns_400(self, create_post_instance, create_post_image_instance, update_post_image):
        image = create_post_image_instance()
        response = update_post_image(image.post_id, image.id, {"image": 'x'})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    
        
    def test_user_is_owner_returns_200(self, create_post_image_instance, update_post_image):
        image = create_post_image_instance()
        
        response = update_post_image(image.post.id, image.id, {"image": image.image, "caption": 'hello'})
        assert response.status_code == status.HTTP_200_OK
        assert response.data['caption'] == 'hello'
@pytest.mark.django_db
class TestPostImageDeletion:
    def test_image_not_found_returns_404(self, create_post_instance, delete_post_image):
        post = create_post_instance()
        response = delete_post_image(post.id, 999)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
    def test_user_is_not_owner_returns_403(self, authenticate, create_post_image_instance, delete_post_image):
        image = create_post_image_instance()
        authenticate()
        response = delete_post_image(image.post_id, image.id)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
    def test_user_is_owner_returns_204(self, create_post_image_instance, delete_post_image):
        image = create_post_image_instance()
        
        response = delete_post_image(image.post_id, image.id)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
      
        
    