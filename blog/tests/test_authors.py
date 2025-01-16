import pytest
from rest_framework import status

@pytest.mark.django_db
class TestAuthorRetrieval:
    def test_author_not_found_returns_404(self,  api_client):
        response = api_client.get('/blog/authors/33/')
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_author_exists_returns_200(self, api_client, authenticate):
        user = authenticate()
        response = api_client.get(f'/blog/authors/{user.author.id}/')
        assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
class TestAuthorProfileEndpoint:
    def test_anonymous_user_cannot_update_profile_returns_401(self, api_client):
        response = api_client.put('/blog/authors/me/', {'bio': 'x'})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_authenticated_user_can_update_profile_returns_200(self, api_client, authenticate):
        authenticate()
        response = api_client.put('/blog/authors/me/', {'bio': 'x'})
        assert response.status_code == status.HTTP_200_OK


