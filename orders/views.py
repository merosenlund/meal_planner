import io
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView, CreateView
from django.views.generic.list import ListView
from django.urls import reverse, reverse_lazy
from django.http import FileResponse
from datetime import datetime

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

from meals.models import Meal
from orders.models import Order
from orders.forms import (
    MealOrderForm,
    OrderUpdateForm
)


class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "orders/list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["section"] = "orders"
        return context


class OrderCreateView(LoginRequiredMixin, CreateView):
    model = Order
    fields = ["date"]
    template_name = "orders/create.html"

    def get_success_url(self):
        return reverse("update_order", args=[self.object.id])


class OrderUpdateView(LoginRequiredMixin, UpdateView):
    model = Order
    form_class = OrderUpdateForm
    template_name = "orders/update.html"
    success_url = reverse_lazy("orders")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["meal_form"] = MealOrderForm()
        context["section"] = "orders"
        meal_count = context["meal_form"].fields["meals"].queryset.count()
        context["no_meals"] = meal_count == 0
        return context


@login_required
def add_meals_to_order(request, pk):
    if request.method == "POST":
        form = MealOrderForm(request.POST)
        if form.is_valid():
            meals = form.cleaned_data["meals"]
            order = Order.objects.get(pk=pk)
            for meal in meals:
                meal.order = order
                meal.save()
    return redirect(reverse("update_order", args=[pk]))


@login_required
def remove_meal_from_order(request, pk, meal_pk):
    meal = Meal.objects.get(pk=meal_pk)
    order = Order.objects.get(pk=pk)
    order.meals.remove(meal)
    return redirect(reverse("update_order", args=[pk]))


@login_required
def print_orders(request):
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
    from reportlab.platypus import Paragraph, Frame, Table, TableStyle

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.setTitle("Order List")
    p.setFont("Helvetica", 10)

    today = datetime.now().date()
    orders = Order.objects.filter(date__gte=today)

    styles = getSampleStyleSheet()
    title_style = styles["Title"]

    for order in orders:
        story = []

        story.append(Paragraph("Purchase Order", title_style))

        header_data = [
            ["Order #:", order.id]
        ]
        header_table = Table(
            header_data,
            colWidths=("*", 1.5*inch),
            spaceAfter=0.5*inch,
            spaceBefore=0.5*inch
        )

        header_table.setStyle(TableStyle([
            ("ALIGN", (0, 0), (0, -1), "RIGHT"),
            ("LINEBELOW", (1, 0), (1, -1), 0.25, colors.black),
        ]))

        story.append(header_table)

        ingredient_data = [[
            "Ingredients",
            "Amount",
            "Have",
            "Need",
        ]]

        ingredients = order.get_ingredients()

        for ingredient, [amount, uom] in ingredients.items():
            ingredient_data.append([
                ingredient.title(),
                f"{amount} {uom}",
            ])

        ingredient_table = Table(
            ingredient_data, colWidths=(4*inch, "*", "*", "*")
        )
        ingredient_table.setStyle(TableStyle([
            ("BOX", (0, 0), (-1, -1), 0.25, colors.black),
            ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.black),
            ("LINEBELOW", (0, 0), (-1, 0), 2, colors.black),
            ("LINEBELOW", (0, 0), (-1, 0), 2, colors.black),
            ("ALIGN", (1, 0), (-1, 0), "CENTER")
        ]))

        story.append(ingredient_table)
        f = Frame(0.5*inch, 0.5*inch, 7.5*inch, 10*inch)
        f.hAlign = "LEFT"
        f.addFromList(story, p)
        p.showPage()

    p.save()

    buffer.seek(0)
    return FileResponse(buffer, filename='orders.pdf')
