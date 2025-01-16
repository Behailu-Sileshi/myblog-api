import pytest
from rest_framework import status
from model_bakery import baker
from django.core.files.uploadedfile import SimpleUploadedFile
from blog.models import PostVideo

BASE_POST_URL = '/blog/posts/'

# Fixtures
@pytest.fixture
def upload_post_video(api_client):
    def do_upload_post_video(post_id, data):
        return api_client.post(f"{BASE_POST_URL}{post_id}/videos/", data, format='multipart')
    return do_upload_post_video

@pytest.fixture
def retrieve_post_video(api_client):
    def do_retrieve_post_video(post_id, video_id):
        return api_client.get(f"{BASE_POST_URL}{post_id}/videos/{video_id}/")
    return do_retrieve_post_video

@pytest.fixture
def update_post_video(api_client):
    def do_update_post_video(post_id, video_id, data):
        return api_client.put(f"{BASE_POST_URL}{post_id}/videos/{video_id}/", data, format='multipart')
    return do_update_post_video

@pytest.fixture
def delete_post_video(api_client):
    def do_delete_post_video(post_id, video_id):
        return api_client.delete(f"{BASE_POST_URL}{post_id}/videos/{video_id}/")
    return do_delete_post_video

@pytest.fixture
def create_upload_video():
    def do_create_upload_video():
        with open('blog/tests/file/demo.mp4', 'rb') as video_file:
            uploaded_video = SimpleUploadedFile(
                "demo.mp4",
                video_file.read(),
                content_type="video/mp4"
            )
        return uploaded_video
    return do_create_upload_video

@pytest.fixture
def create_post_video_instance(create_upload_video, create_post_instance):
    def do_create_post_video_instance():
        post = create_post_instance()
        video = create_upload_video()
        return baker.make(PostVideo, post_id=post.id, video=video)
    return do_create_post_video_instance

# Test Classes
@pytest.mark.django_db
class TestPostVideoCreation:
    def test_anonymous_user_cannot_upload_returns_401(self, api_client, create_post_instance, upload_post_video, create_upload_video):
        post = create_post_instance()
        api_client.logout()
        upload_video = create_upload_video()
        response = upload_post_video(post.id, {"video": upload_video})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_user_not_owner_cannot_upload_returns_403(self, authenticate, create_post_instance, upload_post_video, create_upload_video):
        post = create_post_instance()
        authenticate()
        upload_video = create_upload_video()
        response = upload_post_video(post.id, {"video": upload_video})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_invalid_data_returns_400(self, create_post_instance, upload_post_video):
        post = create_post_instance()
        response = upload_post_video(post.id, {"video": 'x'})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_valid_data_creates_video_returns_201(self, authenticate, create_post_instance, upload_post_video, create_upload_video):
        post = create_post_instance()
        upload_video = create_upload_video()
        response = upload_post_video(post.id, {"video": upload_video})
        assert response.status_code == status.HTTP_201_CREATED
        assert 'id' in response.data and response.data['id'] > 0

@pytest.mark.django_db
class TestPostVideoRetrieval:
    def test_video_not_found_returns_404(self, create_post_instance, retrieve_post_video):
        post = create_post_instance()
        response = retrieve_post_video(post.id, 999)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_video_found_returns_200(self, create_post_video_instance, retrieve_post_video):
        video = create_post_video_instance()
        response = retrieve_post_video(video.post_id, video.id)
        assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
class TestPostVideoUpdate:
    
    def test_video_not_found_returns_404(self, create_post_instance, update_post_video):
        post = create_post_instance()
        response = update_post_video(post.id, 999, {})
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_user_is_not_owner_returns_403(self, authenticate, create_post_video_instance, update_post_video):
        video = create_post_video_instance()
        authenticate()
        response = update_post_video(video.post_id, video.id, {'video': video.video, 'caption': 'hello'})
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
    def test_invalid_data_returns_400(self, create_post_instance, create_post_video_instance, update_post_video):
        video = create_post_video_instance()
        response = update_post_video(video.post_id, video.id, {"video": 'x'})
        assert response.status_code == status.HTTP_400_BAD_REQUEST


    def test_user_is_owner_returns_200(self, authenticate, create_post_video_instance, update_post_video):
        video = create_post_video_instance()
        response = update_post_video(video.post_id, video.id, {"video": video.video, "caption": 'updated caption'})
        assert response.status_code == status.HTTP_200_OK
        assert response.data['caption'] == 'updated caption'

@pytest.mark.django_db
class TestPostVideoDeletion:
    
    def test_video_not_found(self, create_post_instance, delete_post_video):
        post = create_post_instance()
        response = delete_post_video(post.id, 999)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_user_is_not_owner_returns_403(self, authenticate, create_post_video_instance, delete_post_video):
        video = create_post_video_instance()
        authenticate()
        response = delete_post_video(video.post_id, video.id)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_user_is_owner_returns_204(self, create_post_video_instance, delete_post_video):
        video = create_post_video_instance()
        response = delete_post_video(video.post_id, video.id)
        assert response.status_code == status.HTTP_204_NO_CONTENT
