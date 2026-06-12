# Uncomment the required imports before adding the code

# from django.shortcuts import render
# from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
# from django.shortcuts import get_object_or_404, render, redirect
# from django.contrib.auth import logout
# from django.contrib import messages
# from datetime import datetime

from django.http import JsonResponse
from django.contrib.auth import login, authenticate, logout
import logging
import json
from django.views.decorators.csrf import csrf_exempt
from .models import CarMake, CarModel
from .populate import initiate
from .restapis import get_request, analyze_review_sentiments, post_review


# Get an instance of a logger
logger = logging.getLogger(__name__)

DEALERS = [
    {"id": 1, "full_name": "Holdlamis Car Dealership", "city": "El Paso",
        "address": "3 Nova Court", "zip": "88563", "state": "Texas"},
    {"id": 2, "full_name": "Temp Car Dealership", "city": "Minneapolis",
        "address": "6337 Butternut Crossing", "zip": "55402", "state": "Minnesota"},
    {"id": 3, "full_name": "Sub-Ex Car Dealership", "city": "Birmingham",
        "address": "9477 Twin Pines Center", "zip": "35285", "state": "Alabama"},
    {"id": 4, "full_name": "Solarbreeze Car Dealership", "city": "Houston",
        "address": "580 Delladonna Circle", "zip": "75241", "state": "Texas"},
    {"id": 5, "full_name": "Regrant Car Dealership", "city": "Baltimore",
        "address": "93 Golf Course Pass", "zip": "21203", "state": "Maryland"},
    {"id": 6, "full_name": "Stronghold Car Dealership", "city": "Pittsburgh",
        "address": "2 Hawthorne Lane", "zip": "18763", "state": "Pennsylvania"},
    {"id": 7, "full_name": "Job Car Dealership", "city": "Pueblo",
        "address": "9 Cambridge Park", "zip": "81010", "state": "Colorado"},
    {"id": 8, "full_name": "Bytecard Car Dealership", "city": "Topeka",
        "address": "288 Larry Place", "zip": "66642", "state": "Kansas"},
    {"id": 9, "full_name": "Job Car Dealership", "city": "Dallas",
        "address": "253 Hanson Junction", "zip": "75216", "state": "Texas"},
    {"id": 10, "full_name": "Alphazap Car Dealership", "city": "Washington",
        "address": "108 Memorial Pass", "zip": "20005", "state": "District of Columbia"},
    {"id": 11, "full_name": "Tresom Car Dealership", "city": "Austin",
        "address": "7 Green Ridge Street", "zip": "78732", "state": "Texas"},
    {"id": 12, "full_name": "Tin Car Dealership", "city": "Silver Spring",
        "address": "20 Lerdahl Lane", "zip": "20908", "state": "Maryland"},
    {"id": 13, "full_name": "Y-Solowarm Car Dealership", "city": "Baltimore",
        "address": "4 Fairview Place", "zip": "21215", "state": "Maryland"},
    {"id": 34, "full_name": "Gembucket Car Dealership", "city": "Silver Spring",
        "address": "8 Golf Hill", "zip": "20904", "state": "Maryland"},
    {"id": 41, "full_name": "Tres-Zap Car Dealership", "city": "Baltimore",
        "address": "9 Sherman Hill", "zip": "21275", "state": "Maryland"},
]

REVIEWS = [
    {
        "id": 1,
        "dealership": 1,
        "name": "lauvshree",
        "review": "Fantastic Dealership.",
        "purchase": True,
        "purchase_date": "2023-01-12",
        "car_make": "NISSAN",
        "car_model": "Qashqai",
        "car_year": 2023,
        "sentiment": "positive",
    },
    {
        "id": 2,
        "dealership": 1,
        "name": "lauvshree",
        "review": "Great Service. Highly recommended.",
        "purchase": True,
        "purchase_date": "2023-01-12",
        "car_make": "NISSAN",
        "car_model": "XTRAIL",
        "car_year": 2023,
        "sentiment": "positive",
    },
]


# Create your views here.

# Create a `login_request` view to handle sign in request
@csrf_exempt
def login_user(request):
    # Get username and password from request.POST dictionary
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    # Try to check if provide credential can be authenticated
    user = authenticate(username=username, password=password)
    data = {"userName": username}
    if user is not None:
        # If user is valid, call login method to login current user
        login(request, user)
        data = {"userName": username, "status": "Authenticated"}
    return JsonResponse(data)

# Create a `logout_request` view to handle sign out request


def logout_request(request):
    logout(request)
    data = {"userName": ""}
    return JsonResponse(data)

# Create a `registration` view to handle sign up request


@csrf_exempt
def registration(request):
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    first_name = data['firstName']
    last_name = data['lastName']
    email = data['email']

    if User.objects.filter(username=username).exists():
        return JsonResponse({"userName": username, "error": "Already Registered"})

    user = User.objects.create_user(
        username=username,
        password=password,
        first_name=first_name,
        last_name=last_name,
        email=email,
    )
    login(request, user)
    return JsonResponse({"userName": username, "status": "Authenticated"})

# # Update the `get_dealerships` view to render the index page with
# a list of dealerships


def get_dealerships(request, state="All"):
    if(state == "All"):
        endpoint = "/fetchDealers"
    else:
        endpoint = "/fetchDealers/"+state
    dealerships = get_request(endpoint)
    if dealerships is None:
        dealerships = DEALERS if state == "All" else [
            dealer for dealer in DEALERS if dealer["state"] == state
        ]
    return JsonResponse({"status":200,"dealers":dealerships})


def get_dealer_details(request, dealer_id):
    if(dealer_id):
        endpoint = "/fetchDealer/"+str(dealer_id)
        dealership = get_request(endpoint)
        if dealership is None:
            dealership = [
                dealer for dealer in DEALERS if dealer["id"] == dealer_id
            ]
        return JsonResponse({"status":200,"dealer":dealership})
    else:
        return JsonResponse({"status":400,"message":"Bad Request"})


def get_cars(request):
    count = CarMake.objects.filter().count()
    if count == 0:
        initiate()
    car_models = CarModel.objects.select_related('car_make')
    cars = []
    for car_model in car_models:
        cars.append({
            "CarModel": car_model.name,
            "CarMake": car_model.car_make.name,
        })
    return JsonResponse({"CarModels": cars})

# Create a `get_dealer_reviews` view to render the reviews of a dealer


def get_dealer_reviews(request, dealer_id):
    if(dealer_id):
        endpoint = "/fetchReviews/dealer/"+str(dealer_id)
        reviews = get_request(endpoint)
        if reviews is None:
            reviews = [
                review for review in REVIEWS
                if int(review["dealership"]) == dealer_id
            ]
        for review_detail in reviews:
            response = analyze_review_sentiments(review_detail['review'])
            if response is not None:
                review_detail['sentiment'] = response['sentiment']
            elif 'sentiment' not in review_detail:
                review_detail['sentiment'] = 'neutral'
        return JsonResponse({"status":200,"reviews":reviews})
    else:
        return JsonResponse({"status":400,"message":"Bad Request"})

# Create a `get_dealer_details` view to render the dealer details

# Create a `add_review` view to submit a review


@csrf_exempt
def add_review(request):
    if(request.user.is_anonymous == False):
        data = json.loads(request.body)
        try:
            response = post_review(data)
            if response is None:
                review = data.copy()
                review["id"] = max([item["id"] for item in REVIEWS], default=0) + 1
                review["dealership"] = int(review["dealership"])
                review["car_year"] = int(review["car_year"])
                sentiment = analyze_review_sentiments(review["review"])
                review["sentiment"] = (
                    sentiment["sentiment"] if sentiment is not None else "neutral"
                )
                REVIEWS.append(review)
            return JsonResponse({"status": 200})
        except:
            return JsonResponse({"status": 401, "message": "Error in posting review"})
    else:
        return JsonResponse({"status": 403, "message": "Unauthorized"})
