from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from bs4 import BeautifulSoup
import requests
from requests.exceptions import JSONDecodeError
from .models import *
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .forms import CustomerRegistrationForm, CustomerLoginForm, PostForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from OnlinerClone.context_processors import *
from django.db.models import F
from django.db.models import Q
from faker import Faker
import certifi


# Create your views here.
def index(request):
    url_weather = r'https://rp5.by/%D0%9F%D0%BE%D0%B3%D0%BE%D0%B4%D0%B0_%D0%B2_%D0%9C%D0%B8%D0%BD%D1%81%D0%BA%D0%B5,_%D0%91%D0%B5%D0%BB%D0%B0%D1%80%D1%83%D1%81%D1%8C'
    # website
    response_temperature = requests.get(url_weather, verify=False).text
    soup_temperature = BeautifulSoup(response_temperature, 'html.parser')
    temperature_html_tag = soup_temperature.find("div", class_="ArchiveTemp")
    temperature_html_tag = temperature_html_tag.find("span", class_="t_0")
    temperature_value = temperature_html_tag.get_text(strip=True)
    print(temperature_value.split(' ')[0])
    temperature_int = float(temperature_value.split(' ')[0])

    url_exrate_usd = r'https://api.nbrb.by/exrates/rates/USD?parammode=2'
    url_exrate_eur = r'https://api.nbrb.by/exrates/rates/EUR?parammode=2'
    response_exrate_usd = requests.get(url_exrate_usd).json()
    response_exrate_eur = requests.get(url_exrate_eur).json()
    exrate_value_usd = round(response_exrate_usd["Cur_OfficialRate"], 2)
    exrate_value_eur = round(response_exrate_eur["Cur_OfficialRate"], 2)

    print(exrate_value_usd, exrate_value_eur)

    url_news = r'https://www.ixbt.com/news/'
    response_news = requests.get(url_news).text
    soup_news = BeautifulSoup(response_news, 'html.parser')
    news_ul_list = soup_news.find("div", class_="b-block b-block__newslistdefault b-lined-title")
    news_ul_list_recent = news_ul_list.find_all("ul")[0]
    news_ul_list_previous = news_ul_list.find_all("ul")[1]
    top3_news = {}
    for i in range(len(news_ul_list_recent.find_all("li"))):
        temp = news_ul_list_recent.find_all("li")[i]
        time = temp.find("span", class_="time_iteration_icon_light").get_text(strip=True)
        title = temp.find("strong").get_text(strip=True)
        subtitle = temp.find("div", class_="item__text__top").get_text(strip=True)
        try:
            a = temp.find_all("a")[1]
            href = r'https://www.ixbt.com' + a.get('href')
        except IndexError:
            a = temp.find_all("a")[0]
            href = r'https://www.ixbt.com' + a.get('href')
        top3_news_dict = {
            "newsNo": i + 1,
            "time_released": time,
            "title": title,
            "subtitle": subtitle,
            "href": href
        }

        top3_news[i + 1] = top3_news_dict

        # all_news.append(news_ul_list_recent.find_all("li")[i])
    print(top3_news)
    other_news = {}
    for i in range(len(news_ul_list_previous.find_all("li"))):
        temp = news_ul_list_previous.find_all("li")[i]
        time = temp.find("span", class_="time_iteration_icon_light").get_text(strip=True)
        title = temp.find("strong").get_text(strip=True)

        href = None

        try:
            subtitle = temp.find_all("a")[1].get_text(strip=True)
            a = temp.find_all("a")[1]
            href = r'https://www.ixbt.com' + a.get('href')
        except IndexError:
            subtitle = temp.find("strong").get_text(strip=True)
            a = temp.find_all("a")[0]
            href = r'https://www.ixbt.com' + a.get('href')
            print(subtitle, 'NOT_FOUND')
        other_news_dict = {
            "newsNo": i + 1,
            "time_released": time,
            "title": title,
            "subtitle": subtitle,
            "href": href
        }

        other_news[i + 1] = other_news_dict

    print(other_news)

    today = datetime.today().date()
    # Calculate yesterday's date
    yesterday = today - timedelta(days=1)
    # Initialize the previous time as None
    previous_time = None
    # Iterate through the times in the existing order
    for news in other_news.values():
        time_str = news["time_released"]
        current_time = datetime.strptime(time_str, "%H:%M").time()

        if previous_time is not None and previous_time > current_time:
            # Previous time is later than the current time, set PREVIOUS_DATE to yesterday's date
            previous_date = yesterday
            break

        previous_time = current_time
    else:
        # All times are in the correct order, set PREVIOUS_DATE to today's date
        previous_date = today

    print(previous_date)
    print(temperature_value)
    print(temperature_int)
    if request.user.is_authenticated:
        unseen_messages_count_all = Chat.objects.filter(users=request.user, messages__status='unseen')
        unseen_messages_count_sent_by_me = Chat.objects.filter(users=request.user, messages__status='unseen',
                                                               messages__sender=request.user)

        unseen_messages_count_sent_to_me = unseen_messages_count_all.exclude(
            id__in=unseen_messages_count_sent_by_me.values('id')).distinct()
        count_unseen_messages_sent_to_me = unseen_messages_count_sent_to_me.count()


    context = {
        "temperature_now": temperature_value, "temperature_int": temperature_int, "exrate_now_usd": exrate_value_usd,
        "exrate_now_eur": exrate_value_eur,
        "top3_news": top3_news, "other_news": other_news, "previous_date": previous_date,
    }
    return render(request, "index.html", context=context)




def base_view(request):
    context = {
    }
    return render(request, 'base.html', context)


def customer_registration(request):
    if request.method == 'POST':
        customer_registration_form = CustomerRegistrationForm(request.POST)
        if customer_registration_form.is_valid():
            # Если форма регистрации клиента действительна, получаем данные из формы
            username = customer_registration_form.cleaned_data.get("username")
            password = customer_registration_form.cleaned_data.get("password")
            email = customer_registration_form.cleaned_data.get("email")

            if User.objects.filter(username=username).exists():
                # Проверяем, существует ли пользователь с таким именем пользователя
                customer_registration_form.add_error('username', "Такое имя пользователя уже существует.")
            else:
                # Если пользователь с таким именем пользователя не существует, создаем нового пользователя
                user = User.objects.create_user(username, email, password)

                # Создаем новый объект Customer и связываем его с созданным пользователем
                customer = Customer(user=user)
                customer.full_name = customer_registration_form.cleaned_data.get("full_name")
                customer.address = customer_registration_form.cleaned_data.get("address")
                customer.save()

                # Аутентифицируем пользователя
                login(request, user)

                return redirect("home")
    else:
        customer_registration_form = CustomerRegistrationForm()

    # Создаем контекст с формой регистрации клиента и передаем его в шаблон
    context = {'customer_registration_form': customer_registration_form}
    return render(request, 'customer_registration.html', context=context)


def customer_logout(request):
    # Выход пользователя из системы
    logout(request)
    return redirect("home")


def customer_login(request):
    if request.method == 'POST':
        customer_login_form = CustomerLoginForm(request.POST)
        if customer_login_form.is_valid():
            # Если метод запроса POST и форма входа пользователя действительна, получаем данные из формы
            username = customer_login_form.cleaned_data.get("username")
            password = customer_login_form.cleaned_data.get("password")

            # Аутентификация пользователя
            user = authenticate(username=username, password=password)

            if user is not None and user.customer:
                # Если пользователь существует и является клиентом, аутентифицируем пользователя и перенаправляем на
                # домашнюю страницу
                login(request, user)
                return redirect("home")
            else:
                # Если пользователь не существует или не является клиентом, отображаем ошибку входа
                context = {'customer_login_form': CustomerLoginForm, 'error': 'Данные введены неверно'}
                return render(request, 'customer_login.html', context)
    else:
        customer_login_form = CustomerLoginForm()

    # Создаем контекст с формой входа пользователя и передаем его в шаблон
    context = {'customer_login_form': customer_login_form}
    return render(request, 'customer_login.html', context=context)


def market(request):
    posts = Post.objects.all()

    # Apply filters
    category_id = request.GET.get('category')
    if category_id:
        posts = posts.filter(category_id=category_id)

    # Apply sorting
    sort_option = request.GET.get('sort')
    if sort_option == 'asc':
        posts = posts.order_by('price')
    elif sort_option == 'desc':
        posts = posts.order_by('-price')
    elif sort_option == 'popular':
        posts = posts.order_by('-views')
    elif sort_option == 'least_popular':
        posts = posts.order_by('views')

    # Apply search
    search_query = request.GET.get('search')
    search_description = request.GET.get('search_in_desc')
    if search_query:
        if search_description:
            fuzzy_posts = []
            for post in posts:
                post_text = post.title + ' ' + post.description
                if all(word.lower() in post_text.lower() for word in search_query.split()):
                    fuzzy_posts.append(post)
            posts = fuzzy_posts
        else:
            fuzzy_posts = []
            for post in posts:
                if all(word.lower() in post.title.lower() for word in search_query.split()):
                    fuzzy_posts.append(post)
            posts = fuzzy_posts

    context = {
        'posts': posts,
        'categories': Categories.objects.all(),
        'search_query': search_query if search_query else '',  # Set search_query to empty string if None
        'search_description': search_description,  # Add search_description to the context
        'category_id': int(category_id) if category_id else None,  # Convert category_id to int and set to None if None
        'sort_option': sort_option  # Add sort_option to the context
    }
    return render(request, 'market.html', context=context)


@login_required(login_url='login')
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.created_by = request.user
            post.save()
            return redirect("market")
    else:
        form = PostForm()
    context = {
        'form': form
    }
    return render(request, 'create_post.html', context=context)


@login_required(login_url='login')
def my_posts(request):
    posts = Post.objects.filter(created_by=request.user)

    context = {
        'posts': posts
    }
    return render(request, 'my_posts.html', context=context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    # Check if the user has already viewed the post
    viewed_posts = request.session.get('viewed_posts', [])
    if post_id not in viewed_posts:
        # Increment the view count and mark the post as viewed
        post.views += 1
        post.save()
        viewed_posts.append(post_id)
        request.session['viewed_posts'] = viewed_posts

    context = {
        'post': post
    }
    return render(request, 'post_detail.html', context=context)


@login_required(login_url='login')
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, created_by=request.user)

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('my_posts')
    else:
        form = PostForm(instance=post)

    context = {
        'form': form,
        'post': post
    }
    return render(request, 'edit_post.html', context=context)


@login_required(login_url='login')
def open_chat(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    # Check if a chat already exists between the two users
    chat = Chat.objects.filter(users=request.user).filter(users=other_user).first()

    if chat is not None:
        # Retrieve unseen messages for the recipient
        unseen_messages = Message.objects.filter(chat=chat, sender=other_user, status='unseen')

        # Update the status of unseen messages to 'seen'
        unseen_messages.update(status='seen')

        # Render the chat template
        return render(request, 'chat.html', {'chat': chat, 'other_user': other_user})

    # Check if the logged-in user is the same as the other user
    if request.user == other_user:
        return HttpResponse("You cannot open a chat with yourself.")

    # If no chat exists, create a new one
    chat = Chat.objects.create()
    chat.users.add(request.user, other_user)

    return render(request, 'chat.html', {'chat': chat, 'other_user': other_user})


@login_required(login_url='login')
def send_message(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    content = request.POST.get('content')
    if content:
        Message.objects.create(chat=chat, sender=request.user, content=content)
    # Use the users field of the chat to determine the redirect URL
    other_user = chat.users.exclude(id=request.user.id).first()
    return redirect('open_chat', user_id=other_user.id)


@login_required(login_url='login')
def chats(request):
    user_chats = Chat.objects.filter(users=request.user)
    unseen_messages_count_all = Chat.objects.filter(users=request.user, messages__status='unseen')
    unseen_messages_sent_by_me = Chat.objects.filter(users=request.user, messages__status='unseen',
                                                     messages__sender=request.user)
    chats_with_unseen_messages_sent_to_me = unseen_messages_count_all.exclude(
        id__in=unseen_messages_sent_by_me.values('id'))

    chat_unseen_message_count = {}
    chat_last_unread_message = {}

    for chat in user_chats:
        unseen_messages_by_me_count = chats_with_unseen_messages_sent_to_me.filter(id=chat.id).count()
        chat_unseen_message_count[chat.id] = unseen_messages_by_me_count

        if unseen_messages_by_me_count > 0:
            last_unread_message = chat.messages.filter(status='unseen').last()
            chat_last_unread_message[chat.id] = last_unread_message

    context = {
        'user_chats': user_chats,
        'chat_unseen_message_count': chat_unseen_message_count,
        'chat_last_unread_message': chat_last_unread_message,
    }

    return render(request, 'chats.html', context=context)
