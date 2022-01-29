from django.shortcuts import render


# Create your views here.
def meal_list(request):
    return render(request, "meals/meal_list.html")
