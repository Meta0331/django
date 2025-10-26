from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Product, Category, Supplier


# ---------------- AUTHENTICATION ----------------

@login_required
def home(request):
    # Redirect based on user type
    if request.user.is_superuser:
        return redirect('pages:admin_dashboard')
    elif request.user.is_staff:
        return redirect('pages:cashier_dashboard')
    else:
        return redirect('pages:cashier_dashboard')


def authView(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST or None)
        if form.is_valid():
            form.save()
            return redirect('pages:login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {"form": form})


def custom_login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)

            # Redirect based on user type
            if user.is_superuser:
                return redirect('pages:admin_dashboard')
            elif user.is_staff:
                return redirect('pages:cashier_dashboard')
            else:
                return redirect('pages:cashier_dashboard')
    else:
        form = AuthenticationForm()

    return render(request, 'registration/login.html', {"form": form})


@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect('pages:cashier_dashboard')
    return render(request, 'admin/admin_dashboard.html', {})


@login_required
def cashier_dashboard(request):
    return render(request, 'cashier/cashier_dashboard.html', {})


# ---------------- PRODUCT & CATEGORY MANAGEMENT ----------------

@login_required
def products(request):
    query = request.GET.get('q')
    category_id = request.GET.get('category')

    products = Product.objects.all().order_by('id')

    # --- FILTER BY SEARCH QUERY ---
    if query:
        products = products.filter(product_name__icontains=query)

    # --- FILTER BY CATEGORY ---
    selected_category = None
    if category_id:
        try:
            category = Category.objects.get(id=category_id)
            selected_category = category
            products = products.filter(product_category=category.name)
        except Category.DoesNotExist:
            pass

    categories = Category.objects.all()
    suppliers = Supplier.objects.all()  # ✅ Fetch suppliers here

    # --- PAGINATION ---
    paginator = Paginator(products, 10)
    page_number = request.GET.get('page')
    products_page = paginator.get_page(page_number)

    current_page = products_page.number
    total_pages = paginator.num_pages
    start = max(1, current_page - 2)
    end = min(total_pages, current_page + 2)
    page_range = range(start, end + 1)

    # --- ADD CATEGORY FUNCTIONALITY ---
    if request.method == "POST" and 'add_category' in request.POST:
        category_name = request.POST.get('category_name')
        if category_name:
            Category.objects.get_or_create(name=category_name)
        return redirect('pages:products')

    return render(request, 'admin/products.html', {
        'products': products_page,
        'paginator': paginator,
        'page_range': page_range,
        'categories': categories,
        'selected_category': selected_category,
        'suppliers': suppliers,  # ✅ Pass to template
    })




@login_required
def add_product(request):
    if request.method == "POST":
        name = request.POST.get('name')
        price = request.POST.get('price')
        quantity = request.POST.get('quantity')
        category_id = request.POST.get('category')
        image = request.FILES.get('image')

        # Find category object if exists
        category = None
        if category_id:
            try:
                category = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                category = None

        Product.objects.create(
            product_name=name,
            product_price=price,
            product_quantity=quantity,
            product_category=category.name if category else '',
            product_img=image
        )
        return redirect('pages:products')
    return redirect('pages:products')


@login_required
def edit_product(request, id):
    product = get_object_or_404(Product, id=id)
    if request.method == "POST":
        product.product_name = request.POST.get('name')
        product.product_price = request.POST.get('price')
        product.product_quantity = request.POST.get('quantity')

        category_id = request.POST.get('category')
        if category_id:
            try:
                category = Category.objects.get(id=category_id)
                product.product_category = category.name
            except Category.DoesNotExist:
                pass

        if request.FILES.get('image'):
            product.product_img = request.FILES.get('image')

        product.save()
        return redirect('pages:products')

    return render(request, 'admin/edit_product.html', {'product': product})


@login_required
def delete_product(request, id):
    product = get_object_or_404(Product, id=id)
    product.delete()
    return redirect('pages:products')

def users(request):
    return render(request, 'admin/users.html')


# ✅ Add Category
def add_category(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Category.objects.create(name=name)
            messages.success(request, f'Category "{name}" added successfully!')
    return redirect('pages:products')


# ✅ Edit Category (POST only — no missing template)
def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        new_name = request.POST.get('name')
        if new_name:
            category.name = new_name
            category.save()
            messages.success(request, f'Category renamed to "{new_name}" successfully!')
    return redirect('pages:products')


# ✅ Delete Category (and all its products)
def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    # Delete all products with this category
    Product.objects.filter(product_category=category.name).delete()
    category.delete()
    messages.warning(request, f'Category "{category.name}" and all its products have been deleted!')
    return redirect('pages:products')


def suppliers(request):
    suppliers = Supplier.objects.all()
    total_suppliers = suppliers.count()
    active_suppliers = suppliers.filter(is_active=True).count()
    return render(request, 'admin/suppliers.html', {
        'suppliers': suppliers,
        'total_suppliers': total_suppliers,
        'active_suppliers': active_suppliers
    })


def add_supplier(request):
    if request.method == 'POST':
        Supplier.objects.create(
            name=request.POST['name'],
            contact=request.POST.get('contact', ''),
            email=request.POST.get('email', ''),
            address=request.POST.get('address', ''),
            company=request.POST.get('company', '')
        )
        return redirect('pages:suppliers')
    return redirect('pages:suppliers')

def edit_supplier(request, supplier_id):
    supplier = get_object_or_404(Supplier, id=supplier_id)
    if request.method == 'POST':
        supplier.name = request.POST['name']
        supplier.contact = request.POST.get('contact', '')
        supplier.email = request.POST.get('email', '')
        supplier.address = request.POST.get('address', '')
        supplier.company = request.POST.get('company', '')
        supplier.save()
        return redirect('pages:suppliers')
    return redirect('pages:suppliers')

def delete_supplier(request, supplier_id):
    supplier = get_object_or_404(Supplier, id=supplier_id)
    supplier.delete()
    return redirect('pages:suppliers')


@login_required
def restock_product(request, id):
    product = get_object_or_404(Product, id=id)
    suppliers = Supplier.objects.all()  # ✅ Fetch all suppliers

    if request.method == "POST":
        try:
            restock_qty = int(request.POST.get("restock_qty", 0))
            supplier_id = request.POST.get("supplier")

            if restock_qty > 0:
                product.product_quantity += restock_qty
                product.save()

                supplier = None
                if supplier_id:
                    try:
                        supplier = Supplier.objects.get(id=supplier_id)
                    except Supplier.DoesNotExist:
                        supplier = None

                # ✅ Save to Restock table
                from .models import Restock
                Restock.objects.create(
                    product=product,
                    supplier=supplier,
                    quantity_added=restock_qty
                )

                messages.success(
                    request,
                    f"{product.product_name} restocked by {restock_qty} units."
                )
            else:
                messages.error(request, "Please enter a valid quantity.")
        except ValueError:
            messages.error(request, "Invalid quantity entered.")

        return redirect('pages:products')

    # ✅ If GET request, render restock modal or page
    return render(request, 'admin/restock_product.html', {
        'product': product,
        'suppliers': suppliers
    })
