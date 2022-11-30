from django.core.paginator import Paginator
from posts.constants import PER_PAGE


def paginate_page(request, posts):
    paginator = Paginator(posts, PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
