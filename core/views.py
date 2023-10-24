from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from .models import Project, Innovation, Contribution, Reward_Payment, Make_Investment, Transaction, DepositMoney, Withdrawal, SendMoney, WithdrawProjectFunds
from django_countries import countries
from .forms import CreateProjectForm, CreateInnovationForm, MakeContributionForm, MyInvestmentForm, InvestmentStatusForm, StatementTypeForm, WithdrawalRequestAuthorizationForm
from accounts.models import Innovator, Moderator, BaseUser
from django.utils import timezone
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import uuid, requests, os, json
from dotenv import load_dotenv
from django.utils.dateparse import parse_datetime
from itertools import chain

load_dotenv()


# Create your views here.
def home(request):
    print('TIME: ', timezone.now())
    return render(request, 'index.html')

def add_project(request):
    project_creation_request = ''
    if request.method == 'POST':
        create_project_form = CreateProjectForm(request.POST or None, request.FILES or None)
        if create_project_form.is_valid():
            project_obj = create_project_form.save(commit=False)
            project_obj.innovator = Innovator.objects.get(user__username=request.user.username)
            # project_obj.date_created = timezone.now()
            # print('BEFORE: ', project_obj.business_type)
            # print('BEFORE: ', len(project_obj.business_type))
            project_obj.business_type = list(project_obj.business_type.replace("[", "").replace("]", "").replace("'", "").replace('"', ''))
            # print('AFTER: ', project_obj.business_type)
            # print('AFTER: ', len(project_obj.business_type))
            if create_project_form.cleaned_data['innovator_user_agreement']:
                project_obj.innovator_user_agreement = True
            project_obj.save()
            # print('TIME: ', project_obj.date_created)
            project_creation_request = 'Thank you for submitting your project details. Your project creation request has been sent to a moderator for review. A moderator will carefully assess your project to ensure that the provided information aligns with our user agreement and complies with legal regulations. Please allow some time for our team to review your project thoroughly. We appreciate your patience. If there are any additional details or documents required, a moderator will reach out to you for clarification. We value your commitment to our platform and look forward to the possibility of bringing your project to our community. Once again, thank you for choosing our platform to showcase your project, and we will be in touch with you soon.'

        else:
            print(create_project_form.errors.as_data())
    else:
        create_project_form = CreateProjectForm()
    return render(request, 'core/add-project.html', {'countries': countries, 'create_project_form': create_project_form, 'project_creation_request': project_creation_request})

def pagination(request, items_list, num_of_pages):
    # if 'from_expected_return' in request.session:
    #     del request.session['from_expected_return']
    # if 'to_expected_return' in request.session:
    #     del request.session['to_expected_return']
    page_number = request.GET.get('page', 1)
    project_paginator = Paginator(items_list.order_by('-pk'), num_of_pages)
    try:
        projects = project_paginator.page(page_number)
    except PageNotAnInteger:
        projects = project_paginator.page(1)
    except EmptyPage:
        projects = project_paginator.page(project_paginator.num_pages)
    return projects


def projects_list(request):
    context = {}
    # print('ON RE: ', request.META.get('HTTP_REFERER'))
    if request.GET.get('from_expected_return'):
        from_expected_return = request.GET.get('from_expected_return')
        context['from_expected_return'] = from_expected_return
        request.session['from_expected_return'] = from_expected_return
        to_expected_return = request.GET.get('to_expected_return')
        context['to_expected_return'] = to_expected_return
        request.session['to_expected_return'] = to_expected_return

        if from_expected_return:
            # print('FROM: ', from_expected_return)
            if to_expected_return:
                # print('TO: ', to_expected_return)
                projects = Project.objects.filter(
                    Q(expected_return__range=(int(from_expected_return), int(to_expected_return)))
                )
                # projects = pagination(request, projects, 4)
            else:
                projects = Project.objects.filter(
                    Q(expected_return__gte=int(from_expected_return))
                )
                projects = pagination(request, projects, 4)
            context['projects'] = projects
    else:
        # request.GET
        projects = Project.objects.all()
        projects = pagination(request, projects, 4)
        context['projects'] = projects
    return render(request, 'core/projects.html', context)

def project_details(request, project_pk):
    context = {}
    project = Project.objects.get(pk=project_pk)
    context['project'] = project
    # if not request.user.is_authenticated:
    #     return redirect('accounts:innovator_login')
    try:
        if request.user.is_innovator:
            # print('2')
            investor_1 = Innovator.objects.get(user__pk=request.user.pk)
            context['investor_1'] = investor_1

            if request.method == 'POST' and 'date-filter' in request.POST:
                # print('3')
                date_from = request.POST.get('date-from')
                date_to = request.POST.get('date-to')
                investors = Make_Investment.objects.filter(investment__pk=project_pk, date_sent__date__range=(date_from, date_to))
                context['date_from'] = date_from
                context['date_to'] = date_to
            else:
                investors = Make_Investment.objects.filter(investment__pk=project_pk).order_by('-date_sent')
                # context['transaction'] = Transaction.objects.filter(owner__user__pk=request.user.pk).order_by('-date_generated')[0]
                # print('4')
            context['investors'] = investors

        else:
            # print('5')
            moderator = Moderator.objects.get(user__pk=request.user.pk)
            context['moderator'] = moderator
            # print('YO: ', request.POST.get('status'))
            status_form = InvestmentStatusForm()
            # print('STATUS_FORM: ', status_form)
            # print('brev')
            context['status_form'] = status_form
            if request.method == 'POST'and 'status' in request.POST:
                project.status = request.POST.get('status')
                project.save()
                # print('broo: ', project.status)
                messages.success(request, 'Investment details has been updated!')
    except:
        pass
    return render(request, 'core/project_details.html', context)

def add_innovation(request):
    context = {}
    if not request.user.is_authenticated:
        return redirect('accounts:innovator_login')
    try:
        innovator = Innovator.objects.get(user=request.user.pk)
    except:
        return HttpResponse("Sorry! You do not have an Innovator's privileges")
    if request.method == 'POST':
        add_innovation_form = CreateInnovationForm(request.POST or None, request.FILES or None)
        if add_innovation_form.is_valid():
            context['title'] = add_innovation_form.cleaned_data['title']
            context['reward'] = add_innovation_form.cleaned_data['reward']
            if not Innovation.objects.filter(title=request.POST.get('title'), owner=innovator.pk).exists():
                innovation_object = add_innovation_form.save(commit=False)
                innovation_object.owner = innovator
                innovation_object.save()
                context['add_innovation_success'] = 'Innovation has been submitted. A moderator will reach out to you soon.'
                return redirect('home')
            else:
                context['innovation_unique_error'] = 'You have already created a similar innovation.'
        else:
            print('ERRORS: ', add_innovation_form.errors.as_data())
    else:
        add_innovation_form = CreateInnovationForm()
    context['add_innovation_form'] = add_innovation_form
    return render(request, 'core/add-innovation.html', context)

def innovations_list(request):
    context = {}
    innovations = Innovation.objects.all().order_by('date_created')
    innovations = pagination(request, innovations, 4)
    context['innovations'] = innovations
    return render(request, 'core/innovations-list.html', context)

def innovation_detail(request, pk):
    context = {}
    innovation = Innovation.objects.get(pk=pk)
    context['contributions'] = Contribution.objects.filter(innovation__pk=pk)
    context['innovation'] = Innovation.objects.get(pk=pk)

    if request.method == 'POST' and 'contribute' in request.POST:
        if not request.user.is_authenticated:
            return redirect('accounts:innovator_login')
        contribution_form_data = {
            'contribution': request.POST.get('contribution')
        }
        contribution_form = MakeContributionForm(contribution_form_data)
        if contribution_form.is_valid():
            obj = contribution_form.save(commit=False)
            obj.innovation = Innovation.objects.get(pk=pk)
            obj.contributor = Innovator.objects.get(user__pk=request.user.pk)
            obj.innovation.num_of_contributions += 1
            obj.innovation.save()
            obj.save()
            messages.success(request, 'Hurray. Your comment has been posted!')
            return redirect('innovation_details', pk)
    else:
        contribution_form = MakeContributionForm()
    context['contribution_form'] = contribution_form
    return render(request, 'core/innovation-details.html', context)


@login_required
def upvote_contribution(request, contribution_pk):
    contribution = Contribution.objects.get(pk=contribution_pk)
    user = Innovator.objects.get(user__pk=request.user.pk)
    # print('ALL: ', contribution.upvoted_by.all())

    # Check if the user has already upvoted this contribution
    if user in contribution.upvoted_by.all():
        return JsonResponse({'error': 'You have already upvoted this contribution'})

    # Check if the user has previously downvoted and remove the downvote
    elif user in contribution.downvoted_by.all() and user not in contribution.upvoted_by.all():
        contribution.downvoted_by.remove(user)
        if contribution.downvotes == -1:
            contribution.downvotes = 0
        else:
            contribution.downvotes += 1
        contribution.upvotes += 1
        contribution.upvoted_by.add(user)
        contribution.save()
    elif user not in contribution.upvoted_by.all() and user not in contribution.downvoted_by.all():
        contribution.upvoted_by.add(user)
        contribution.upvotes += 1
        contribution.save()
    return JsonResponse({'upvotes': contribution.upvoted_by.count()})

@login_required
def downvote_contribution(request, contribution_pk):
    contribution = Contribution.objects.get(pk=contribution_pk)
    user = Innovator.objects.get(user__pk=request.user.pk)

    # Check if the user has already downvoted this contribution
    if user in contribution.downvoted_by.all():
        return JsonResponse({'error': 'You have already downvoted this contribution'})

    # Check if the user has previously upvoted and remove the upvote
    elif user in contribution.upvoted_by.all() and user not in contribution.downvoted_by.all():
        contribution.upvoted_by.remove(user)
        contribution.upvotes -=1
        if contribution.downvotes == 0:
            contribution.downvotes = -1
        else:
            contribution.downvotes -= 1
        contribution.downvoted_by.add(user)
        contribution.save()
    elif user not in contribution.upvoted_by.all() and user not in contribution.downvoted_by.all():
        contribution.downvoted_by.add(user)
        contribution.downvotes -= 1
        contribution.save()
    return JsonResponse({'downvotes': contribution.downvoted_by.count()})

@login_required
def accept_contribution(request, contribution_pk):
    if Contribution.objects.get(pk=contribution_pk).innovation.owner.user.pk == request.user.pk:
        contribution = Contribution.objects.get(pk=contribution_pk)
        contribution.accepted = True
        contribution.save()
        return redirect('innovation_details', contribution.innovation.pk)
    return render(request, 'core/innovation-details.html', {'contribution': contribution})


@login_required
def unaccept_contribution(request, contribution_pk):
    if Contribution.objects.get(pk=contribution_pk).innovation.owner.user.pk == request.user.pk:
        contribution = Contribution.objects.get(pk=contribution_pk)
        contribution.accepted = False
        contribution.save()
        return redirect('innovation_details', contribution.innovation.pk)
    return render(request, 'core/innovation-details.html', {'contribution': contribution})

@login_required
def deposit_money(request):
    context = {}
    banks = requests.get(f"https://api.paystack.co/bank")
    context['banks'] = banks.json()['data']
    user = BaseUser.objects.get(pk=request.user.pk)
    innovator = Innovator.objects.get(user__pk=user.pk)
    if request.method == 'POST' and 'amount' in request.POST:
        print('BREV')
        deposit_money = DepositMoney.objects.create(
            amount=request.POST.get('amount'),
            innovator = Innovator.objects.get(user__pk=request.user.pk)
        )
        deposit_money = DepositMoney.objects.get(pk=deposit_money.pk)
        if request.POST.get('bool') == 'True':
            if deposit_money.innovator.account_balance is None:
                deposit_money.innovator.account_balance = 0
            # print('MAN')
            # print('AMount: ', request.POST.get('amount'))
            deposit_money.pre_balance = innovator.account_balance
            deposit_money.innovator.account_balance += int(request.POST.get('amount'))
            deposit_money.innovator.save()
            deposit_money.post_balance = innovator.account_balance + int(request.POST.get('amount'))
            deposit_money.save()
            innovator = Innovator.objects.get(user__email=request.user.email)
            transaction = Transaction.objects.create(
                owner=innovator,
                description= f"You deposited ₦{request.POST.get('amount')} into your account",
                successful = not False,
                reference_code = deposit_money.reference_code,
                amount = int(request.POST.get('amount')),
                pre_balance = innovator.account_balance - int(request.POST.get('amount')),
                post_balance = innovator.account_balance,
                type='DEPOSIT'
            )
            context['transaction'] = Transaction.objects.filter(owner__user__pk=request.user.pk).order_by('-date_generated')[0]
            # print(innovator.account_balance)
            # print('DONDA')
            return redirect('projects')
        else:
            print('Transaction could not be completed')
        # print('DONE')
    context['user'] = user
    context['innovator'] = innovator
    return render(request, 'core/fund.html', context)

# @login_required
# def make_investment_payment(request, investment_pk):
#     context = {}
#     investment = Project.objects.get(pk=investment_pk)
#     # if request.POST.get('bool') == 'True':
#     if request.method == 'POST' and 'pay' in request.POST:
#         make_payment = Make_Investment.objects.create(
#             send_to = Innovator.objects.get(user__email=investment.innovator.user.email),
#             send_from = Innovator.objects.get(user__pk=request.user.pk),
#             sender = Innovator.objects.get(user__pk=request.user.pk),
#             amount = request.POST.get('amount'),
#             investment = Project.objects.get(pk=investment_pk),
#             expected_return=request.POST.get('amount')*investment.expected_return
#         )
#         request.session['pk'] = investment.pk
#         investment.target -= int(make_payment.amount)
#         if investment.fund_raised is None:
#             investment.fund_raised = 0
#         investment.fund_raised += int(make_payment.amount)
#         if investment.amount_left is None:
#             investment.amount_left = investment.target
#         investment.amount_left -= int(make_payment.amount)
#         investment.save()
#         context['make_payment'] = make_payment
#         transaction = Transaction.objects.create(
#                 owner=Innovator.objects.get(user__email=investment.innovator.user.email),
#                 description= f"You deposited ₦{request.POST.get('amount')} into your CrowdSourceIt",
#                 successful = not False,
#                 reference_code = invest.reference_code,
#                 amount = request.POST.get('amount')
#             )
#         # return HttpResponse('Your payment is being proceesed!')
#         return redirect('projects')
#     # else:
#     #     return HttpResponse('Your payment could not be authenticated')
#     context['investment'] = investment
#     return render(request, 'core/project_details.html', context)

@login_required
def invest(request, investment_pk):
    context = {}
    investment = Project.objects.get(pk=investment_pk)
    investor = Innovator.objects.get(user__pk=request.user.pk)
    context['investor_1'] = investor
    investment_owner = investment.innovator
    context['project'] = investment
    if request.method == 'POST' and 'invest' in request.POST:
        amount = int(request.POST.get('amount'))
        if amount <= investor.account_balance:
            # if request.user.username == investment_owner.user.username:
            # else:
            investor.account_balance -= amount
            investor.save()
            # print('ACCOUNT BALANCE: ', investor.account_balance)
            investment.target -= amount
            # if investment_owner.account_balance is None:
            #     investment_owner.account_balance = 0
            # investment_owner.account_balance += amount
            # investment_owner.save()

            if investment.fund_raised is None:
                investment.fund_raised = 0
            investment.fund_raised += amount
            if investment.amount_left == 0 and investment.fund_raised:
                investment.complete = True
            investment.save()
            invest = Make_Investment.objects.create(
                send_to=investment.innovator,
                send_from=investor,
                sender=investor,
                amount=amount,
                investment=investment,
                expected_return=amount*investment.expected_return
            )
            transaction = Transaction.objects.create(
                owner=investor,
                description= f"You have invested ₦{amount} in {investment.name}",
                successful = not False,
                reference_code = invest.reference_code,
                amount = amount,
                pre_balance = investor.account_balance + amount,
                post_balance = investor.account_balance,
                type='OUTGOING INVESTMENT'
            )
            transaction = Transaction.objects.create(
                owner=investment_owner,
                description= f"Investor {investor.user.username} invested ₦{amount} in your project --{investment.name}",
                successful = not False,
                reference_code = invest.reference_code,
                amount = amount,
                pre_balance = investment.fund_raised - amount,
                post_balance = investment.fund_raised,
                type='INCOMING INVESTMENT'
            )
            context['transaction'] = Transaction.objects.filter(owner__user__pk=request.user.pk).order_by('-date_generated')[0]
            messages.success(request, 'Thank you for investing in this project!')
            return redirect('project_details', investment_pk)
        else:
            return HttpResponse('Insufficient Account Balance ')
    return render(request, 'core/project_details.html', context)


@login_required
def investments(request):
    investments = Project.objects.filter(innovator__user__pk=request.user.pk)
    return render(request, 'core/investments.html', {'investments': investments})

@login_required
def my_investments(request):
    context = {}
    
    context['category_form'] = MyInvestmentForm()
    if request.method == 'POST' and 'filter_investments' in request.POST:
        print('WHY, MAN!!!')
        investment_date_from = request.POST.get('investment_date_from')
        investment_date_to = request.POST.get('investment_date_to')
        investment_categories = request.POST.getlist('business_type')
        context['investment_date_from'] = investment_date_from
        context['investment_date_to'] = investment_date_to
        context['investment_categories'] = investment_categories


        if investment_date_from and not investment_date_to and not investment_categories:
            my_investments = Make_Investment.objects.filter(sender__user__pk=request.user.pk, date_sent__gte=investment_date_from)
            context['my_investments'] = my_investments
        elif investment_date_from and investment_date_to and not investment_categories:
            my_investments = Make_Investment.objects.filter(sender__user__pk=request.user.pk, date_sent__date__range=(investment_date_from, investment_date_to))
            context['my_investments'] = my_investments
        elif investment_date_from and not investment_date_to and investment_categories:
            my_investments = Make_Investment.objects.filter(sender__user__pk=request.user.pk, date_sent__gte=investment_date_from, investment__business_type__icontains=investment_categories[0])
            context['my_investments'] = my_investments
        elif investment_date_from and investment_date_to and investment_categories:
            my_investments = Make_Investment.objects.filter(sender__user__pk=request.user.pk, date_sent__date__range=(investment_date_from, investment_date_to), investment__business_type__icontains=investment_categories[0])
            context['my_investments'] = my_investments
        elif not investment_date_from and not investment_date_to and investment_categories:
            my_investments = Make_Investment.objects.filter(sender__user__pk=request.user.pk, investment__business_type__icontains=investment_categories[0])
            context['my_investments'] = my_investments
        context['category_form'] = MyInvestmentForm({'business_type': request.POST.get('business_type')})
    else:
        my_investments = Make_Investment.objects.filter(sender__user__pk=request.user.pk)
        context['my_investments'] = my_investments
    return render(request, 'core/my-investments.html', context)

def statement(request):
    context = {}
    context['statement_type_form'] = StatementTypeForm()
    if request.method == 'POST' and 'filter_statement' in request.POST:
        statement_date_from = parse_datetime(request.POST.get('statement_date_from'))
        statement_date_to = parse_datetime(request.POST.get('statement_date_to'))
        type_list = request.POST.getlist('type')
        context['statement_date_from'] = statement_date_from
        context['statement_date_to'] = statement_date_to
        # print('TYPE LIST: ', type_list)
        if statement_date_from != None and statement_date_to != None and len(type_list) > 0:
            context['transactions'] = Transaction.objects.filter(
                type__in=type_list,
                owner__user__pk=request.user.pk,
                date_generated__date__range=(statement_date_from, statement_date_to),
                ).order_by('-date_generated')
        elif statement_date_from != None and statement_date_to != None and len(type_list) == 0:
            context['transactions'] = Transaction.objects.filter(
                owner__user__pk=request.user.pk,
                date_generated__date__range=(statement_date_from, statement_date_to),
                ).order_by('-date_generated')
        elif statement_date_from != None and statement_date_to == None and len(type_list) > 0:
            context['transactions'] = Transaction.objects.filter(
                type__in=type_list,
                owner__user__pk=request.user.pk,
                date_generated__gte=(statement_date_from),
                ).order_by('-date_generated')
        elif statement_date_from != None and statement_date_to == None and len(type_list) == 0:
            context['transactions'] = Transaction.objects.filter(
                owner__user__pk=request.user.pk,
                date_generated__gte=(statement_date_from),
                ).order_by('-date_generated')
        elif statement_date_from == None and statement_date_to == None and len(type_list) > 0:
            context['transactions'] = Transaction.objects.filter(
                type__in=type_list,
                owner__user__pk=request.user.pk
                ).order_by('-date_generated')
        elif statement_date_from == None and statement_date_to == None and len(type_list) == 0:
            context['transactions'] = Transaction.objects.filter(
                owner__user__pk=request.user.pk
                ).order_by('-date_generated')
        context['statement_type_form'] = StatementTypeForm({'type': type_list})
    else:
        context['transactions'] = Transaction.objects.filter(owner__user__pk=request.user.pk).order_by('-date_generated')
    return render(request, 'core/statement.html', context)

def get_bank_details(request):
    amount = request.POST.get('withdraw_amount')
    # print('AMOUNT: ', amount)
    account_number = request.POST.get('withdraw_to')
    # print('ACCOUNT NUMBER: ', account_number)
    bank_code = request.POST.get('bank_code')
    # print('BANK CODE', bank_code)
    bank_name = ''
    banks = requests.get(f"https://api.paystack.co/bank")
    banks = banks.json()['data']
    for bank in banks:
        if bank['code'] == bank_code:
            bank_name = bank['name']
            # request.session['bank_name'] = bank_name
    request.session['amount'] = amount
    request.session['account_number'] = account_number
    request.session['bank_code'] = bank_code
    if request.method == 'POST':
        url = f"https://api.paystack.co/bank/resolve?account_number={account_number}&bank_code={bank_code}"
        headers = {
            "Authorization": f"Bearer {os.environ.get('PAYSTACK_SECRET_KEY')}"
        }
        response = requests.get(url, headers=headers)
        # print('GET BANK DETAILS RESPONSE: ', response)
        if response.status_code == 200:
            withdrawal_data = response.json()
            request.session['account_holder'] = withdrawal_data['data']['account_name']
            data = {
                'account_data': withdrawal_data['data'],
                'bank_code': bank_code,
                'bank_name': bank_name,
                'status': 'success',
                'withdraw_amount': amount,
            }
            return JsonResponse(data, status=200)
        else:
            print("Request failed with status code:", response.status_code)
            # print("Response content:", response.text)
            return JsonResponse({'error': 'Error encountered while retrieving bank account details.', 'status': 'failed'})

def withdraw(request):
    context = {}
    withdraw_amount = int(request.session.get('amount'))
    account_number = request.session.get('account_number')
    bank_code = request.session.get('bank_code')
    banks = requests.get(f"https://api.paystack.co/bank").json()['data']
    bank_name = ''
    for bank in banks:
        if bank['code'] == bank_code:
            bank_name = bank['name']
    url = f"https://api.paystack.co/bank/resolve?account_number={account_number}&bank_code={bank_code}"
    headers = {
        "Authorization": f"Bearer {os.environ.get('PAYSTACK_SECRET_KEY')}"
    }
    response = requests.get(url, headers=headers)
    # print('WITHDRAW RESPONSE: ', response.json())
    innovator = Innovator.objects.get(user__pk=request.user.pk)
    if response.status_code == 200:
        if innovator.account_balance >= withdraw_amount:
            withdrawal = Withdrawal.objects.create(
                amount=withdraw_amount,
                account_number=account_number,
                bank_name=bank_name,
                bank_code=bank_code,
                innovator = Innovator.objects.get(user__pk=request.user.pk),
                account_holder = response.json()['data']['account_name'],
                pre_balance=innovator.account_balance,
                post_balance = innovator.account_balance - withdraw_amount
            )

            Transaction.objects.create(
                owner=Innovator.objects.get(user__pk=request.user.pk),
                description= f"You made a withdrawal of ₦{withdraw_amount} into {account_number}-{bank_name}",
                successful = not False,
                reference_code = withdrawal.reference_code,
                amount = withdraw_amount,
                pre_balance=innovator.account_balance,
                post_balance = innovator.account_balance - withdraw_amount,
                type = 'WITHDRAWAL',
            )
            innovator.account_balance -= withdraw_amount
            innovator.save()
            messages.success(request, 'You have successfully made a request for withdrawal')
            return redirect('home')
        else:
            return HttpResponse('You cannot withdraw more than what you have.')
    return render(request, 'core/fund.html', context)

def send_money(request):
    context = {}
    if request.method == 'POST' and 'send_money' in request.POST:
        sender = Innovator.objects.get(user__username=request.user.username)
        recipient_username = request.POST.get('recipient_username')
        amount_to_send = request.POST.get('amount_to_send')
        if recipient_username is None or recipient_username == '':
            messages.error(request, 'You forgot to provide the username of the recipient')  
        if amount_to_send is None or amount_to_send == '':
            messages.error(request, 'You forgot to enter the amount you want to send')
        elif recipient_username and amount_to_send:
            amount_to_send = int(request.POST.get('amount_to_send'))
            try:
                recipient = Innovator.objects.get(user__username=recipient_username)
                if amount_to_send != 0 and amount_to_send is not None and sender.account_balance >= amount_to_send:
                    amount_to_send = int(amount_to_send)
                    send_money = SendMoney.objects.create(
                        amount = amount_to_send,
                        sender = sender,
                        recipient = recipient,
                        pre_balance = sender.account_balance,
                        post_balance = sender.account_balance - amount_to_send,
                    )
                    sender.account_balance -= amount_to_send
                    sender.save()
                    
                    if recipient.account_balance == None:
                        recipient.account_balance = 0
                    recipient.account_balance += amount_to_send
                    recipient.save()
                    Transaction.objects.create(
                        owner=sender,
                        description= f"You sent ₦{amount_to_send} to {recipient_username} on {send_money.date}",
                        successful = not False,
                        reference_code = send_money.reference_code,
                        amount = amount_to_send,
                        pre_balance = sender.account_balance + amount_to_send,
                        post_balance = sender.account_balance,
                        type = 'OUTGOING TRANSFER'
                    )
                    send_money.create_receive_money_instance()
                    messages.success(request, f'You have successfully sent ₦{amount_to_send} to {recipient.user.username}.')
                    context['send_money_obj'] = send_money
                    context['money_sent'] = 'yes'
                    # del request.session['amount_to_send']
                    # del request.session['recipient_username']
                    return redirect('deposit')
                else:
                    messages.error(request, 'Insufficient Balance')
                    context['money_sent'] = False
            except Innovator.DoesNotExist:
                messages.error(request, 'User does not exist')
            # if not recipient_username:
            #     messages.error(request, 'You forgot to provide the username of the recipient')
    context['amount_to_send'] = request.POST.get('amount_to_send')
    context['recipient_username'] = request.POST.get('recipient_username')
    return render(request, 'core/fund.html', context)

def investment_capital(request):
    context = {}
    banks = requests.get(f"https://api.paystack.co/bank")
    # print('BANKS: ', banks.json())
    context['banks'] = banks.json()['data']
    projects_owned = Project.objects.filter(
        innovator__user__pk=request.user.pk
    )
    context['projects_owned'] = projects_owned
    return render(request, 'core/investment-capital.html', context)

def withdraw_project_funds_page(request):
    context = {}
    return render(request, 'core/withdraw-project-funds-page.html', context)

def withdraw_project_funds(request, project_pk):
    context = {}
    project = Project.objects.get(pk=project_pk)
    withdraw_amount = int(request.session.get('amount'))
    account_number = request.session.get('account_number')
    bank_code = request.session.get('bank_code')
    banks = requests.get(f"https://api.paystack.co/bank").json()['data']
    bank_name = ''
    for bank in banks:
        if bank['code'] == bank_code:
            bank_name = bank['name']
    url = f"https://api.paystack.co/bank/resolve?account_number={account_number}&bank_code={bank_code}"
    headers = {
        "Authorization": f"Bearer {os.environ.get('PAYSTACK_SECRET_KEY')}"
    }
    response = requests.get(url, headers=headers)
    # print('WITHDRAW PROJECT FUNDS RESPONSE: ', response.json())
    innovator = Innovator.objects.get(user__pk=request.user.pk)
    if response.status_code == 200:
        if project.fund_raised >= withdraw_amount:
            withdraw_project_funds = WithdrawProjectFunds.objects.create(
                project = project,
                amount=withdraw_amount,
                account_number=account_number,
                bank_name=bank_name,
                bank_code=bank_code,
                innovator = Innovator.objects.get(user__pk=request.user.pk),
                account_holder = response.json()['data']['account_name'],
                pre_balance=project.fund_raised,
                post_balance = project.fund_raised - withdraw_amount
            )

            Transaction.objects.create(
                owner=Innovator.objects.get(user__pk=request.user.pk),
                description= f"You made a withdrawal of ₦{withdraw_amount} from {project.name}'s funds into {account_number}-{bank_name}",
                successful = not False,
                reference_code = withdraw_project_funds.reference_code,
                amount = withdraw_amount,
                pre_balance=project.fund_raised,
                post_balance = project.fund_raised - withdraw_amount,
                type = 'WITHDRAWAL',
            )
            project.fund_raised -= withdraw_amount
            project.save()
            messages.success(request, f'You have successfully made a request for withdrawal from the {project.name.title()} project funds')
            return redirect('home')
        else:
            return HttpResponse('You cannot withdraw more than what you have.')
    return render(request, 'core/withdraw-project-funds.html', context)

@login_required
def withdrawal_requests(request):
    context = {}
    context['form'] = WithdrawalRequestAuthorizationForm()
    if request.user.is_moderator:
        if request.method == 'POST':
            date_from = parse_datetime(request.POST.get('date_from'))
            date_to = parse_datetime(request.POST.get('date_to'))
            type_list = request.POST.getlist('type')
            context['date_from'] = date_from
            context['date_to'] = date_to
            context['type_list'] = type_list
            # withdrawal_requests = Withdrawal.objects.filter().order_by('-date')
            # project_withdrawal_requests = WithdrawProjectFunds.objects.filter().order_by('-date')
            if date_from != None and date_to != None and len(type_list) > 0:
                context['withdrawal_requests'] = Withdrawal.objects.filter(
                    is_approved__in=type_list,
                    date__date__range=(date_from, date_to),
                    ).order_by('-date')
                context['project_withdrawal_requests'] = WithdrawProjectFunds.objects.filter(
                    is_approved__in=type_list,
                    date__date__range=(date_from, date_to),
                    ).order_by('-date')
            elif date_from != None and date_to != None and len(type_list) == 0:
                context['withdrawal_requests'] = Withdrawal.objects.filter(
                    date__date__range=(date_from, date_to),
                    ).order_by('-date')
                context['project_withdrawal_requests'] = WithdrawProjectFunds.objects.filter(
                    date__date__range=(date_from, date_to),
                    ).order_by('-date')
            elif date_from != None and date_to == None and len(type_list) > 0:
                context['withdrawal_requests'] = Withdrawal.objects.filter(
                    is_approved__in=type_list,
                    date__gte=(date_from),
                    ).order_by('-date')
                context['project_withdrawal_requests'] = WithdrawProjectFunds.objects.filter(
                    is_approved__in=type_list,
                    date__gte=(date_from),
                    ).order_by('-date')
            elif date_from != None and date_to == None and len(type_list) == 0:
                context['withdrawal_requests'] = Withdrawal.objects.filter(
                    date__gte=(date_from),
                    ).order_by('-date')
                context['project_withdrawal_requests'] = WithdrawProjectFunds.objects.filter(
                    date__gte=(date_from),
                    ).order_by('-date')
            elif date_from == None and date_to == None and len(type_list) > 0:
                context['withdrawal_requests'] = Withdrawal.objects.filter(
                    is_approved__in=type_list,
                    ).order_by('-date')
                context['project_withdrawal_requests'] = WithdrawProjectFunds.objects.filter(
                    is_approved__in=type_list,
                    ).order_by('-date')
            elif date_from == None and date_to == None and len(type_list) == 0:
                context['withdrawal_requests'] = Withdrawal.objects.filter().order_by('-date')
                context['project_withdrawal_requests'] = WithdrawProjectFunds.objects.filter().order_by('-date')

            context['form'] = WithdrawalRequestAuthorizationForm(
                {
                    'type': type_list
                }
            )
        else:
            context['withdrawal_requests'] = Withdrawal.objects.filter().order_by('-date')
            context['project_withdrawal_requests'] = WithdrawProjectFunds.objects.filter().order_by('-date')
    else:
        return HttpResponse('You are not authorized to view this page')
    return render(request, 'core/withdrawal-requests.html', context)

def withdrawal_request_detail(request, pk, type):
    context = {}
    if type == 'personal_funds':
        withdrawal_request = Withdrawal.objects.get(pk=pk)
        context['withdrawal_request'] = withdrawal_request
    elif type == 'project_capital_contribution_funds':
        withdrawal_request = WithdrawProjectFunds.objects.get(pk=pk)
        context['withdrawal_request'] = withdrawal_request
    return render(request, 'core/withdrawal-request-detail.html', context)