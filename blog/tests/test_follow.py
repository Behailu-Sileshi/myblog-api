import pytest
from rest_framework import status

@pytest.fixture
def follow_author(api_client):
    def do_follow_author(author_id):
        return api_client.post(f'/blog/follow/{author_id}/', {})
    return do_follow_author

@pytest.fixture
def unfollow_author(api_client):
    def do_unfollow_author(author_id):
        return api_client.delete(f'/blog/unfollow/{author_id}/')
    return do_unfollow_author

@pytest.fixture
def create_author_instance(authenticate):
    def do_create_author_instance():
        user = authenticate()
        return user.author
    return do_create_author_instance

@pytest.mark.django_db
class TestFollowAuthor:
    def test_anonymous_user_cannot_follow_returns_401(self, follow_author):
        response = follow_author(4)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_if_author_not_found_returns_404(self, follow_author, authenticate):
        authenticate()
        response = follow_author(99)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_if_user_already_follows_author_returns_409(self, create_author_instance, follow_author, authenticate):
        author = create_author_instance()
        authenticate()
        follow_author(author.id)
        response = follow_author(author.id)
        assert response.status_code == status.HTTP_409_CONFLICT
    
    def test_user_cannot_follow_self_returns_403(self, authenticate, follow_author):
        user = authenticate()
        response = follow_author(user.author.id)
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_authenticated_user_can_follow_author_returns_201(self, follow_author, authenticate, create_author_instance):
        author = create_author_instance()
        authenticate()
        response = follow_author(author.id)
        assert response.status_code == status.HTTP_201_CREATED

@pytest.mark.django_db
class TestUnfollowAuthor:
    def test_anonymous_user_cannot_unfollow_returns_401(self, unfollow_author):
        response = unfollow_author(4)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_if_author_not_found_returns_404(self, unfollow_author, authenticate):
        authenticate()
        response = unfollow_author(99)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_if_user_not_following_author_returns_404(self, unfollow_author, authenticate, create_author_instance):
        authenticate()
        author = create_author_instance()
        response = unfollow_author(author.id)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_user_can_unfollow_author_returns_200(self, unfollow_author, follow_author, authenticate, create_author_instance):
        author = create_author_instance()
        authenticate()
        follow_author(author.id)
        response = unfollow_author(author.id)
        assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
class TestGetFollow:
    def test_anonymous_user_cannot_view_followers_returns_401(self, api_client):
        response = api_client.get('/blog/followers/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_authenticated_user_can_view_followers_returns_200(self, api_client, authenticate):
        authenticate()
        response = api_client.get('/blog/followers/')
        assert response.status_code == status.HTTP_200_OK

    def test_anonymous_user_cannot_view_followings_returns_401(self, api_client):
        response = api_client.get('/blog/followings/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_authenticated_user_can_view_followings_returns_200(self, api_client, authenticate):
        authenticate()
        response = api_client.get('/blog/followings/')
        assert response.status_code == status.HTTP_200_OK
