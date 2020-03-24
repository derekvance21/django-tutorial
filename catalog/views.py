from django.shortcuts import render

# Create your views here.
from catalog.models import Book, Author, BookInstance, Genre

from django.contrib.auth.decorators import login_required

# --- The two commented lines are how you'd use permission for function-based views --- #
# from django.contrib.auth.decorators import permission_required
# @permission_required('catalog.can_mark_returned')
@login_required
def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    
    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    # The 'all()' is implied by default.
    num_authors = Author.objects.count()

    num_harrypotter_books = Book.objects.filter(title__contains='Harry Potter').count()

    # Number of visits of this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_harrypotter_books': num_harrypotter_books,
        'num_visits': num_visits,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)


from django.views import generic

from django.contrib.auth.mixins import LoginRequiredMixin

class BookListView(LoginRequiredMixin, generic.ListView):
    model = Book
    paginate_by = 5
    # login_url = 'catalog/books/'
    # redirect_field_name = '/catalog/authors/' --> but this doesn't work because base_generic.html has its own URL parameters
    
    def get_context_data(self, **kwargs):
        context = super(BookListView, self).get_context_data(**kwargs)
        context['some_data'] = 'This is just some data'
        return context


class BookDetailView(generic.DetailView):
    model = Book


class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 5


class AuthorDetailView(generic.DetailView):
    model = Author


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')


from django.contrib.auth.mixins import PermissionRequiredMixin

class BorrowedBooksListView(PermissionRequiredMixin, generic.ListView):
    """Class-based view only for librarians listing all borrowed books with their users."""
    permission_required = 'catalog.can_mark_returned'
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_librarian.html'
    
    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')