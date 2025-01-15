from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
import pytest
from faker import Faker
from model_bakery import baker
from blog.models import Post

faker = Faker()



@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def authenticate(api_client):
    def do_authenticate():
        user = get_user_model().objects.create_user(
                    username=faker.unique.user_name(),
                    email=faker.unique.email(),
                    password='test123',
            )
        
        api_client.force_authenticate(user=user)
        return user
    return do_authenticate


@pytest.fixture
def create_post_instance(authenticate):
    def do_create_post_instance(**kwargs):
        user = authenticate()
        return baker.make(Post, owner=user.author, **kwargs)
    return do_create_post_instance


    
