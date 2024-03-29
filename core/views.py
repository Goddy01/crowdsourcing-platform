from django.db.models.functions import Length
from django.contrib.auth.models import AnonymousUser
from chat.models import Group, GroupChat
from django.template import RequestContext
from django.db.models import Q
from django.contrib.auth import login, authenticate, logout
from django.utils.html import strip_tags
from django.template import loader
from notifications.signals import notify
from django.utils.encoding import force_bytes, force_str
from django.conf import settings
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from .models import Project, Innovation, Contribution, Reward_Payment, Make_Investment, Transaction, DepositMoney, Withdrawal, SendMoney, WithdrawProjectFunds, ProjectMilestone
from accounts.models import KBAQuestion
from django_countries import countries
from .forms import CreateProjectForm, CreateInnovationForm, MakeContributionForm, MyInvestmentForm, InvestmentStatusForm, StatementTypeForm, WithdrawalRequestAuthorizationForm, FilterWithdrawalRequestForm, FilterConfirmationClickedForm, KBQForm, ConfirmNINForm, AddMilestoneForm, UpdateMilestoneDetailsForm
from accounts.models import Innovator, Moderator, BaseUser
from django.utils import timezone
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect, csrf_exempt
import uuid, requests, os, json
from dotenv import load_dotenv
from django.utils.dateparse import parse_datetime
from itertools import chain
from django.urls import reverse
import datetime
from django.db.models import Count

load_dotenv()
from_email = settings.EMAIL_HOST_USER

# Create your views here.
def home(request):
    current_date = datetime.date.today()
    context = {}
    new_projects = Project.objects.filter(investment_deadline__gte=current_date, target_reached=False).order_by('-date_created')
    context['new_projects'] = new_projects[:5]

    popular_projects = Project.objects.annotate(num_investors=Count('the_investment')).filter(investment_deadline__gte=current_date, target_reached=False).order_by('-num_investors')
    context['popular_projects'] = popular_projects
    # .num_investors
    return render(request, 'index.html', context)

def contact_us(request):
    return render(request, 'core/contact.html')

@login_required
def add_project(request):
    project_creation_request = ''
    if request.method == 'POST':
        if not request.user.is_verified:
            messages.info(request, 'Your account is not yet verified, so you cannot post investment projects')
            return redirect('accounts:edit_profile')
        create_project_form = CreateProjectForm(request.POST or None, request.FILES or None)
        if create_project_form.is_valid():
            project_obj = create_project_form.save(commit=False)
            project_obj.innovator = Innovator.objects.get(user__username=request.user.username)
            project_obj.amount_left = create_project_form.cleaned_data.get('target')

            if create_project_form.cleaned_data['innovator_user_agreement']:
                project_obj.innovator_user_agreement = True
            project_obj.save()
            messages.info(request, 'Thank you for submitting your investment project. Your investment project creation request has been sent to a moderator for review. A moderator will carefully assess the investment project to ensure that the provided information aligns with our user agreement and complies with legal regulations. Please allow some time for our team to review your project thoroughly. We appreciate your patience. If there are any additional details or documents required, a moderator will reach out to you for clarification. We value your commitment to our platform and look forward to the possibility of bringing your investment project to our community. Once again, thank you for choosing our platform to showcase your investment project, and we will be in touch with you soon.')
            return redirect('add_project')

        else:
            print(create_project_form.errors.as_data())
    else:
        create_project_form = CreateProjectForm()
    return render(request, 'core/add-project.html', {'countries': countries, 'create_project_form': create_project_form, 'project_creation_request': project_creation_request})

def search_projects(request):
    context = {}
    query = request.GET.get('query')
    context['query'] = query
    request.session['project_query'] = query
    if request.method == 'GET':
        if query is not None:
            projects = Project.objects.filter(
                Q(name__icontains=query) | Q(motto__icontains=query)
            ).order_by('-date_created').distinct()
            # if not projects:
            #     request.session['search_projects_no_result'] = True
            #     return redirect('projects')
            projects = pagination(request, projects, 4)
            context['projects'] = projects
            request.session['search_projects_no_result'] = False
        else:
            projects = pagination(request, Project.objects.filter(investment_deadline__gte=datetime.datetime.now(), target_reached=False).order_by('-date_created'), 2)
            context['projects'] = projects
    return render(request, 'core/projects.html', context)


def projects_list(request):
    current_date = datetime.date.today()
    context = {}

    from_expected_return = request.GET.get('from_expected_return')
    to_expected_return = request.GET.get('to_expected_return')

    if from_expected_return:
        request.session['from_expected_return'] = from_expected_return
        request.session['to_expected_return'] = to_expected_return

        context.update({
            'from_expected_return': from_expected_return,
            'to_expected_return': to_expected_return,
        })

        filter_conditions = Q()

        if to_expected_return:
            filter_conditions &= Q(expected_return__range=(int(from_expected_return), int(to_expected_return)))
        else:
            filter_conditions &= Q(expected_return__gte=int(from_expected_return))

        if request.user.is_authenticated and not isinstance(request.user, AnonymousUser):
            if not request.user.is_moderator:
                filter_conditions &= Q(investment_deadline__gte=current_date, target_reached=False)

        projects = Project.objects.filter(filter_conditions).order_by('-date_created')
        projects = pagination(request, projects, 4)

        context['projects'] = projects

    else:
        filter_conditions = Q()

        if request.user.is_authenticated and not isinstance(request.user, AnonymousUser):
            if not request.user.is_moderator:
                filter_conditions &= Q(investment_deadline__gte=current_date, target_reached=False)

        projects = Project.objects.filter(filter_conditions).order_by('-date_created')
        projects = pagination(request, projects, 4)

        context['projects'] = projects

    return render(request, 'core/projects.html', context)

def project_details(request, project_pk):
    from .tasks import send_project_approval_status_task
    context = {}
    request.session['project_pk'] = project_pk
    project = Project.objects.get(pk=project_pk)
    context['project_milestones'] = ProjectMilestone.objects.filter(project__pk=project.pk)
    context['project'] = project
    date_now = datetime.datetime.now().date()
    context['is_past_deadline'] = date_now > project.investment_deadline
    
    if request.user.is_authenticated:
        if request.user.is_innovator:
            investor_1 = Innovator.objects.get(user__pk=request.user.pk)
            context['investor_1'] = investor_1

            if request.method == 'POST' and 'date-filter' in request.POST:
                date_from = request.POST.get('date-from')
                date_to = request.POST.get('date-to')
                investors = Make_Investment.objects.filter(investment__pk=project_pk, date_sent__date__range=(date_from, date_to))
                context['date_from'] = date_from
                context['date_to'] = date_to
            else:
                investors = Make_Investment.objects.filter(investment__pk=project_pk).order_by('-date_sent')
            context['investors'] = investors

        else:
            moderator = Moderator.objects.get(user__pk=request.user.pk)
            context['moderator'] = moderator
            status_form = InvestmentStatusForm()
            context['status_form'] = status_form
            if request.method == 'POST' and 'status' in request.POST:
                project.status = request.POST.get('status')
                project.approved_by = moderator
                if request.POST.get('status').title() == 'Approved':
                    project.is_approved = True
                project.save()
                messages.success(request, 'Investment details has been updated!')
                send_project_approval_status_task.apply_async(
                    kwargs= {
                        'investment_pk': project_pk
                    },
                    countdown=10
                )
    
    return render(request, 'core/project_details.html', context)

@login_required
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
            # context['reward'] = add_innovation_form.cleaned_data['reward']
            # if not Innovation.objects.filter(title__icontains=request.POST.get('title'), owner=innovator.pk).exists():
            innovation_object = add_innovation_form.save(commit=False)
            innovation_object.owner = innovator
            innovation_object.save()
            messages.success(request, 'Innovation has been posted.')
            return redirect('innovations_list')
            # else:
            #     messages.error(request, 'You have already created an innovation with similar title.')
            #     return redirect('add_innovation')
        else:
            print('ERRORS: ', add_innovation_form.errors.as_data())
    else:
        add_innovation_form = CreateInnovationForm()
    context['add_innovation_form'] = add_innovation_form
    return render(request, 'core/add-innovation.html', context)

def innovations_list(request):
    context = {}
    innovations = Innovation.objects.all().order_by('-date_created')
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
    context['is_answered'] = Contribution.objects.filter(innovation__pk=pk, accepted=True).exists()
    return render(request, 'core/innovation-details.html', context)

@login_required
def pay_contributor(request, contribution_pk):
    contribution = Contribution.objects.get(pk=contribution_pk)
    innovation = contribution.innovation

    sender = contribution.innovation.owner
    recipient_username = contribution.contributor.user.username
    amount_to_send = contribution.innovation.reward
    recipient = contribution.contributor

    if amount_to_send != 0 and amount_to_send is not None and sender.account_balance >= amount_to_send:
        send_money = SendMoney.objects.create(
            amount = amount_to_send,
            sender = sender,
            recipient = recipient,
            pre_balance = sender.account_balance,
            post_balance = sender.account_balance - amount_to_send,
            is_approved = False
        )
        current_site = get_current_site(request)
        subject = 'NIN Confirmation'
        html_message = loader.render_to_string(
            'core/confirm_nin.html', {
            'user': BaseUser.objects.get(pk=request.user.pk),
            'domain': current_site.domain,
            'amount': int(amount_to_send),
            'date': datetime.datetime.now(),
            'sender': sender,
            'recipient': recipient,
            'amount_to_send': amount_to_send,
            'send_money_pk': send_money.pk,
            'contribution_pk': contribution.pk
        }, request=request
        )
        to_email = f'{request.user.email}'
        send_mail(subject, message = strip_tags(html_message), from_email=from_email, recipient_list= [to_email], fail_silently=False, html_message=html_message)
        messages.success(request, f'Your request to transfer money to {recipient.user.username} has been received. You will receive an email for confirmation, soon.')
        # Create the link to your one_time_link view, including the unique_token
    else:
        messages.error(request, 'Insufficient Balance')
    return redirect('innovation_details', innovation.pk)

@login_required
def upvote_contribution(request, contribution_pk):
    contribution = Contribution.objects.get(pk=contribution_pk)
    user = Innovator.objects.get(user__pk=request.user.pk)

    # Check if the user has already upvoted this contribution
    if user in contribution.upvoted_by.all():
        return JsonResponse({'error': 'You have already upvoted this contribution'})

    # Check if the user has previously downvoted and remove the downvote
    elif user in contribution.downvoted_by.all() and user not in contribution.upvoted_by.all():
        contribution.downvoted_by.remove(user)
        contribution.downvotes -= 1
        contribution.upvotes += 1
        contribution.upvoted_by.add(user)
        contribution.save()
    elif user not in contribution.upvoted_by.all() and user not in contribution.downvoted_by.all():
        contribution.upvoted_by.add(user)
        contribution.upvotes += 1
        contribution.save()
    return JsonResponse({'upvotes': contribution.upvoted_by.count(), 'downvotes': contribution.downvoted_by.count()})

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
        contribution.downvotes += 1
        contribution.downvoted_by.add(user)
        contribution.save()
    elif user not in contribution.upvoted_by.all() and user not in contribution.downvoted_by.all():
        contribution.downvoted_by.add(user)
        contribution.downvotes += 1
        contribution.save()
    return JsonResponse({'upvotes': contribution.upvoted_by.count(), 'downvotes': contribution.downvoted_by.count()})

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
        deposit_money = DepositMoney.objects.create(
            amount=request.POST.get('amount'),
            innovator = Innovator.objects.get(user__pk=request.user.pk)
        )
        deposit_money = DepositMoney.objects.get(pk=deposit_money.pk)
        if request.POST.get('bool') == 'True':
            if deposit_money.innovator.account_balance is None:
                deposit_money.innovator.account_balance = 0
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
            return redirect('deposit')
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
    from .tasks import send_funding_completed_email_task
    context = {}
    investment = Project.objects.get(pk=investment_pk)
    investor = Innovator.objects.get(user__pk=request.user.pk)
    context['investor_1'] = investor
    investment_owner = investment.innovator
    context['project'] = investment
    if request.method == 'POST' and 'invest' in request.POST:
        if investment.target_reached:
            messages.info(request, 'You cannot invest in this investment project because it has reached its funding goal.')
            return redirect('home')

        amount = int(request.POST.get('amount'))
        if amount <= investor.account_balance:
            # Deduct the amount from the investor's account balance
            investor.account_balance -= amount
            investor.save()

            # Update the investment project details
            # investment.target -= amount
            investment.fund_raised = (investment.fund_raised or 0) + amount
            investment.amount_left = max(0, investment.target - investment.fund_raised)
            investment.save()

            # Check if the investment project is fully funded
            current_investment = Project.objects.get(pk=investment_pk)
            if current_investment.amount_left == 0 and current_investment.fund_raised == current_investment.target:
                current_site = get_current_site(request)
                investment.target_reached = True
                investment.save(update_fields=['target_reached'])

                # SENDS EMAIL ABOUT THAT THE FUNDING GOAL HAS BEEN REACHED TO THE PROJECT OWNER AND THE PROJECT INVESTORS
                send_funding_completed_email_task.apply_async(
                    kwargs= {
                        'investment_pk': investment_pk
                    },
                    countdown=10
                )
                

            # Create investment and transaction records
            invest = Make_Investment.objects.create(
                send_to=investment.innovator,
                send_from=investor,
                sender=investor,
                amount=amount,
                expected_return=amount * investment.expected_return,
                investment=investment,
            )

            # Create investor's transaction record
            transaction = Transaction.objects.create(
                owner=investor,
                description=f"You have invested ₦{amount} in {investment.name}",
                successful=not False,
                reference_code=invest.reference_code,
                amount=amount,
                pre_balance=investor.account_balance + amount,
                post_balance=investor.account_balance,
                type='OUTGOING INVESTMENT',
            )

            # Create project owner's transaction record
            transaction = Transaction.objects.create(
                owner=investment_owner,
                description=f"Investor {investor.user.username} invested ₦{amount} in your project --{investment.name}",
                successful=not False,
                reference_code=invest.reference_code,
                amount=amount,
                pre_balance=investment.fund_raised - amount,
                post_balance=investment.fund_raised,
                type='INCOMING INVESTMENT',
            )

            # Add investor to the investment group
            associated_investments = investment.count_make_investments_instances
            if associated_investments == 1:
                new_group = Group.objects.create(
                    name=f'{investment.name} by {investment.innovator.user.get_full_name()}',
                    description=f'This is the community dedicated to investors who have contributed to the {investment.name} project. Please adhere to our community guidelines. The project owner ({investment.innovator.user.get_full_name()}), will regularly share updates on the progress of the investment project with all members.',
                    investment_project=investment
                )
                new_group.members.add(investment.innovator.user)
                if not new_group.members.filter(pk=investor.user.pk).exists():
                    new_group.members.add(investor.user)
            else:
                group = Group.objects.get(
                    investment_project=investment
                )
                group.members.add(investor.user)

            # Set the latest transaction in the context for display
            context['transaction'] = Transaction.objects.filter(owner__user__pk=request.user.pk).order_by('-date_generated')[0]

            messages.success(request, 'Thank you for investing in this project. You will be added to the investment group chat if this is your first investment in this project.')
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

@login_required
def statement(request):
    context = {}
    context['statement_type_form'] = StatementTypeForm()
    if request.method == 'POST' and 'filter_statement' in request.POST:
        statement_date_from = parse_datetime(request.POST.get('statement_date_from'))
        statement_date_to = parse_datetime(request.POST.get('statement_date_to'))
        is_approved_list = request.POST.getlist('type')
        context['statement_date_from'] = statement_date_from
        context['statement_date_to'] = statement_date_to
        if statement_date_from != None and statement_date_to != None and len(is_approved_list) > 0:
            context['transactions'] = Transaction.objects.filter(
                type__in=is_approved_list,
                owner__user__pk=request.user.pk,
                date_generated__date__range=(statement_date_from, statement_date_to),
                ).order_by('-date_generated')
        elif statement_date_from != None and statement_date_to != None and len(is_approved_list) == 0:
            context['transactions'] = Transaction.objects.filter(
                owner__user__pk=request.user.pk,
                date_generated__date__range=(statement_date_from, statement_date_to),
                ).order_by('-date_generated')
        elif statement_date_from != None and statement_date_to == None and len(is_approved_list) > 0:
            context['transactions'] = Transaction.objects.filter(
                type__in=is_approved_list,
                owner__user__pk=request.user.pk,
                date_generated__gte=(statement_date_from),
                ).order_by('-date_generated')
        elif statement_date_from != None and statement_date_to == None and len(is_approved_list) == 0:
            context['transactions'] = Transaction.objects.filter(
                owner__user__pk=request.user.pk,
                date_generated__gte=(statement_date_from),
                ).order_by('-date_generated')
        elif statement_date_from == None and statement_date_to == None and len(is_approved_list) > 0:
            context['transactions'] = Transaction.objects.filter(
                type__in=is_approved_list,
                owner__user__pk=request.user.pk
                ).order_by('-date_generated')
        elif statement_date_from == None and statement_date_to == None and len(is_approved_list) == 0:
            context['transactions'] = Transaction.objects.filter(
                owner__user__pk=request.user.pk
                ).order_by('-date_generated')
        context['statement_type_form'] = StatementTypeForm({'type': is_approved_list})
    else:
        context['transactions'] = Transaction.objects.filter(owner__user__pk=request.user.pk).order_by('-date_generated')
    return render(request, 'core/statement.html', context)

@login_required
def get_bank_details(request):
    amount = request.POST.get('withdraw_amount')
    account_number = request.POST.get('withdraw_to')
    bank_code = request.POST.get('bank_code')
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
            return JsonResponse({'error': 'Error encountered while retrieving bank account details.', 'status': 'failed'})

@login_required
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

@login_required
def send_money(request):
    from .tasks import send_money_task
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
                if sender.account_balance >= amount_to_send:
                    amount_to_send = int(amount_to_send)
                    domain = get_current_site(request).domain
                    
                    send_money_task.apply_async(
                        kwargs={
                            'amount_to_send': amount_to_send, 
                            'sender_pk': sender.pk, 
                            'recipient_pk': recipient.pk, 
                            'sender_prebalance': sender.account_balance, 
                            'sender_postbalance': sender.account_balance-amount_to_send, 
                            'domain': domain
                        },
                        countdown = 5
                    )

                    messages.success(request, f'Your request to transfer money to {recipient.user.username} has been received. You will receive an email for confirmation, soon.')
                    # Create the link to your one_time_link view, including the unique_token
                else:
                    messages.error(request, 'Insufficient Balance')
                    context['money_sent'] = False
                return redirect('deposit')
            except Innovator.DoesNotExist:
                messages.error(request, 'User does not exist')
                return redirect('deposit')
            # if not recipient_username:
            #     messages.error(request, 'You forgot to provide the username of the recipient')
    context['amount_to_send'] = request.POST.get('amount_to_send')
    context['recipient_username'] = request.POST.get('recipient_username')
    return render(request, 'core/fund.html', context)

@login_required
def investment_capital(request):
    context = {}
    banks = requests.get(f"https://api.paystack.co/bank")
    context['banks'] = banks.json()['data']
    projects_owned = Project.objects.filter(
        innovator__user__pk=request.user.pk
    )
    context['projects_owned'] = projects_owned
    return render(request, 'core/investment-capital.html', context)

@login_required
def withdraw_project_funds_page(request):
    context = {}
    return render(request, 'core/withdraw-project-funds-page.html', context)

@login_required
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

            project.fund_raised -= withdraw_amount
            project.save()

            from .tasks import notify_investors_of_project_fund_withdrawal_task
            notify_investors_of_project_fund_withdrawal_task.apply_async(
                kwargs={
                    'withdrawal_pk': withdraw_project_funds.pk
                },
                countdown = 5
            )
            
            messages.success(request, f'You have successfully made a request for withdrawal from the {project.name.title()} project funds')
            return redirect('home')
        else:
            return HttpResponse('You cannot withdraw more than what you have.')
    return render(request, 'core/withdraw-project-funds.html', context)

# PAYSTACK REAL-TIME TRANSFER FEATURE

# @login_required
# def create_recipient(request):
#     # CREATE TRANSFER RECIPIENT
#     create_recipient_url = "https://api.paystack.co/transferrecipient"

#     headers = {
#         "Authorization": f"Bearer {os.environ.get('PAYSTACK_SECRET_KEY')}",
#         "Content-Type": "application/json",
#     }

#     data = {
#         "type": "nuban",
#         "name": request.session.get('name'),
#         "account_number": request.session.get('account_number'),
#         "bank_code": request.session.get('bank_code'),
#         "currency": "NGN",
#     }

#     response = requests.post(create_recipient_url, headers=headers, json=data)

#     # Check the response status and content
#     if response.status_code == 200 or response.status_code == 201:
#         response = response.json()
#         print("Request successful")
#         print('CREATE RECIPIENT RESPONSE:', response)
#         request.session['recipient_code'] = response['data']['recipient_code']
#         # return JsonResponse(response, status=200)
#         initiate_single_transfer(request)
#     else:
#         print(f"Request failed with status code {response.status_code}")
#         print(response.text)
#         return JsonResponse({'error': f"Request failed with status code {response.status_code}"})

# def initiate_single_transfer(request):

#     # Generate a v4 UUID
#     uuid_obj = uuid.uuid4()

#     # Convert the UUID to a string and truncate to a maximum of 100 characters
#     uuid_reference = str(uuid_obj)[:100]

#     url = "https://api.paystack.co/transfer"

#     data = {
#         "source": "balance",
#         "reason": f"Withdrawal of {request.session.get('amount_authorized')} Granted!!!",
#         "amount": request.session.get('amount_authorized') * 100,
#         'reference': uuid_reference,
#         "recipient": request.session.get('recipient_code')
#     }

#     headers = {
#         "Authorization": f"Bearer {os.environ.get('PAYSTACK_SECRET_KEY')}",
#         "Cache-Control": "no-cache",
#     }

#     response = requests.post(url, data=data, headers=headers)
#     print('INITIATE TF RESPONSE: ', response.json())
#     if response.status_code == 200:
#         request.session['transfer_code'] = response.json()['data']['transfer_code']
#         finalize_transfer(request)
#         print('INITIATE SINGLE TRANSFER RESPONSE: ', response)
#         # return JsonResponse(response.json(), status=200)
#     else:
#         return JsonResponse({'error': "Failed to make the API request"}, status=response.status_code)
    
# def finalize_transfer(request):
#     url = "https://api.paystack.co/transfer/finalize_transfer"
#     authorization = f"Bearer {os.environ.get('PAYSTACK_SECRET_KEY')}"
#     content_type = "application/json"
#     # Generate a v4 UUID
#     uuid_obj = uuid.uuid4()

#     # Convert the UUID to a string and truncate to a maximum of 100 characters
#     otp_code = str(uuid_obj)[:6]
#     data = {
#         "transfer_code": request.session.get('transfer_code'),
#         "otp": otp_code
#     }

#     headers = {
#         "Authorization": authorization,
#         "Content-Type": content_type,
#     }

#     response = requests.post(url, headers=headers, json=data)

#     if response.status_code == 200:
#         response_data = response.json()
#         print('FINAL DATA: ', response_data)
#         # return JsonResponse(response_data)
#     else:
#         error_message = f"Failed to finalize transfer. Status code: {response.status_code}"
#         return JsonResponse({"error": error_message}, status=500)


@login_required
def withdrawal_requests(request):
    context = {}
    context['form'] = FilterWithdrawalRequestForm()
    context['set_is_approved_form'] = WithdrawalRequestAuthorizationForm()
    context['filter_confirmation_form'] = FilterConfirmationClickedForm()
    if request.user.is_moderator:
        if request.method == 'POST' and 'filter_withdrawal_requests' in request.POST:
            date_from = parse_datetime(request.POST.get('date_from'))
            date_to = parse_datetime(request.POST.get('date_to'))
            is_approved_list = request.POST.getlist('is_approved')
            confirmation_list = request.POST.getlist('confirmation_clicked')
            kbq_checkbox = request.POST.get('kbq_checkbox')
            context['kbq_checkbox'] = kbq_checkbox
            context['date_from'] = date_from
            context['date_to'] = date_to
            context['is_approved_list'] = is_approved_list
            context['confirmation_list'] = confirmation_list
            # withdrawal_requests = Withdrawal.objects.filter().order_by('-date')
            # project_withdrawal_requests = WithdrawProjectFunds.objects.filter().order_by('-date')
            withdrawal_filter = Q()  # Initialize an empty filter for Withdrawal
            project_withdrawal_filter = Q()  # Initialize an empty filter for WithdrawProjectFunds

            if date_from is not None and date_to is None:
                withdrawal_filter &= Q(date__gte=(date_from))
                project_withdrawal_filter &= Q(date__gte=(date_from))

            elif date_to is not None and date_to is not None:
                withdrawal_filter &= Q(date__date__range=(date_from, date_to))
                project_withdrawal_filter &= Q(date__date__range=(date_from, date_to))
            
            if len(is_approved_list) > 0:
                withdrawal_filter &= Q(is_approved__in=is_approved_list)
                project_withdrawal_filter &= Q(is_approved__in=is_approved_list)

            if len(confirmation_list) > 0:
                withdrawal_filter &= Q(confirmation_clicked__in=confirmation_list)
                project_withdrawal_filter &= Q(confirmation_clicked__in=confirmation_list)

            if kbq_checkbox:
                # Filter for 'kbq_answer' length greater than one
                withdrawal_filter &= Q(kbq_answer__isnull=False)  # Filters for non-null 'kbq_answer' field
                
                project_withdrawal_filter &= Q(kbq_answer__isnull=False)


            context['withdrawal_requests'] = Withdrawal.objects.filter(withdrawal_filter).order_by('-date')
            context['project_withdrawal_requests'] = WithdrawProjectFunds.objects.filter(project_withdrawal_filter).order_by('-date')
            
            context['form'] = FilterWithdrawalRequestForm(
                {
                    'is_approved': is_approved_list
                }
            )
            context['filter_confirmation_form'] = FilterConfirmationClickedForm(
                {
                    'confirmation_clicked': confirmation_list
                }
            )
        else:
            context['withdrawal_requests'] = Withdrawal.objects.filter().order_by('-date')
            context['project_withdrawal_requests'] = WithdrawProjectFunds.objects.filter().order_by('-date')
    else:
        return HttpResponse('You are not authorized to view this page')
    return render(request, 'core/withdrawal-requests.html', context)

@login_required
def send_withdrawal_request_confirmation_email(request, pk, type):
    context = {}
    moderator = Moderator.objects.get(user__email=request.user.email)
    
    if type == 'personal_funds':
        
        withdrawal_request = Withdrawal.objects.get(pk=pk)
        current_site = get_current_site(request)
        subject = 'Withdrawal Request Confirmation'
        # message = render_to_string('core/withdrawal-confirmation.html', {
        #     'user': withdrawal_request.innovator.user,
        #     'domain': current_site.domain,
        #     'uid': urlsafe_base64_encode(force_bytes(withdrawal_request.innovator.user.pk)),
        # })
        html_message = loader.render_to_string(
            'core/withdrawal-confirmation.html', {
            'user': withdrawal_request.innovator.user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(withdrawal_request.innovator.user.pk)),
            'withdrawal_request': withdrawal_request,
            'type': 'p_f',
            'pk': pk
        }, request=request
        )
        to_email = f'{withdrawal_request.innovator.user.email}'
        send_mail(subject, message = strip_tags(html_message), from_email=from_email, recipient_list= [to_email], fail_silently=False, html_message=html_message)
        request.session['withdrawal_request_pk'] = withdrawal_request.pk
        request.session['withdrawal_request_type'] = 'p_f'
        request.session.save()
        
        context['withdrawal_request'] = withdrawal_request
        messages.success(request, 'Confirmation email has successfully been sent. ✅')
        return redirect('withdrawal_requests')
    elif type == 'project_capital_contribution_funds':
        withdrawal_request = WithdrawProjectFunds.objects.get(pk=pk)
        current_site = get_current_site(request)
        subject = 'Withdrawal Request Confirmation'
        # message = render_to_string('core/withdrawal-confirmation.html', {
        #     'user': withdrawal_request.innovator.user,
        #     'domain': current_site.domain,
        #     'uid': urlsafe_base64_encode(force_bytes(withdrawal_request.innovator.user.pk)),
        # })
        html_message = loader.render_to_string(
            'core/withdrawal-confirmation.html', {
            'user': withdrawal_request.innovator.user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(withdrawal_request.innovator.user.pk)),
            'withdrawal_request': withdrawal_request,
            'type': 'p_c_c_f',
            'pk': pk
        }, request=request
        )
        to_email = f'{withdrawal_request.innovator.user.email}'
        send_mail(subject, message = strip_tags(html_message), from_email=from_email, recipient_list= [to_email], fail_silently=False, html_message=html_message)
        request.session['withdrawal_request_pk'] = withdrawal_request.pk
        request.session['withdrawal_request_type'] = 'p_c_c_f'
        request.session.save()
        context['withdrawal_request'] = withdrawal_request
        messages.success(request, 'Confirmation email has successfully been sent. ✅')
        return redirect('withdrawal_requests')
    return render(request, 'core/withdrawal-requests.html', context)

@login_required
def set_withdrawal_request_status(request, pk, type):
    request.session['mandem'] = 'yo'
    context = {}
    moderator = Moderator.objects.get(user__email=request.user.email)
    context['set_is_approved_form'] = WithdrawalRequestAuthorizationForm()
    if request.method == 'POST' and 'set_status' in request.POST:
        is_approved = request.POST.get('is_approved')
        print('TYPE: ', is_approved)
        if type == 'personal_funds':
            withdrawal_request = Withdrawal.objects.get(pk=pk)
            if is_approved == 'True':
                if not withdrawal_request.confirmation:
                    current_site = get_current_site(request)
                    subject = 'Withdrawal Request Confirmation'
                    # message = render_to_string('core/withdrawal-confirmation.html', {
                    #     'user': moderator,
                    #     'domain': current_site.domain,
                    #     'uid': urlsafe_base64_encode(force_bytes(moderator.pk)),
                    # })
                    html_message = loader.render_to_string(
                        'core/withdrawal-confirmation.html', {
                        'user': withdrawal_request.innovator.user,
                        'domain': current_site.domain,
                        'uid': urlsafe_base64_encode(force_bytes(withdrawal_request.innovator.user.pk)),
                    }
                    )
                    to_email = f'{withdrawal_request.innovator.user.email}'
                    send_mail(subject, from_email, [to_email], fail_silently=False, html_message=html_message)
                    # request.session['withdrawal_request_pk'] = withdrawal_request.pk
                else:
                    withdrawal_request.is_approved = not withdrawal_request.is_approved
                    withdrawal_request.save()
            else:
                withdrawal_request.is_approved = False
                withdrawal_request.save()
            context['withdrawal_request'] = withdrawal_request
            return redirect('withdrawal_requests')
        elif type == 'project_capital_contribution_funds':
            withdrawal_request = WithdrawProjectFunds.objects.get(pk=pk)
            if is_approved == 'True':
                if not withdrawal_request.confirmation:
                    current_site = get_current_site(request)
                    subject = 'Activate your account'
                    # message = render_to_string('core/withdrawal-confirmation.html', {
                    #     'user': moderator,
                    #     'domain': current_site.domain,
                    #     'uid': urlsafe_base64_encode(force_bytes(moderator.pk)),
                    # })
                    html_message = loader.render_to_string(
                        'core/withdrawal-confirmation.html', {
                        'user': withdrawal_request.innovator.user,
                        'domain': current_site.domain,
                        'uid': urlsafe_base64_encode(force_bytes(withdrawal_request.innovator.user.pk)),
                    }
                    )
                    to_email = f'{withdrawal_request.innovator.user.email}'
                    send_mail(subject, from_email, [to_email], fail_silently=False)
                    # request.session['withdrawal_request_pk'] = withdrawal_request.pk
                else:
                    withdrawal_request.is_approved = not withdrawal_request.is_approved
                    withdrawal_request.save()
            else:
                withdrawal_request.is_approved = False
                withdrawal_request.save()
            context['withdrawal_request'] = withdrawal_request
            return redirect('withdrawal_requests')
        context['set_is_approved_form'] = WithdrawalRequestAuthorizationForm(
            {
                'is_approved': is_approved
            }
        )
    return render(request, 'core/withdrawal-requests.html', context)

@login_required
def confirm_withdrawal_request(request, type, withdrawal_pk, response):
    if not request.user.is_authenticated:
        return redirect('accounts:innovator_login')
    if type == 'p_f':
        withdrawal_request = Withdrawal.objects.get(pk=withdrawal_pk)
        if not withdrawal_request.confirmation_clicked:
            if response == 'yes':
                withdrawal_request.confirmation = True
                withdrawal_request.confirmation_clicked = True
                withdrawal_request.save()
                return HttpResponse('Thanks for your confirmation. Payment will be made soon.')
            else:
                innovator = Innovator.objects.get(pk=withdrawal_request.innovator.pk)
                innovator.account_balance += withdrawal_request.amount
                innovator.save(update_fields=['account_balance'])
                
                withdrawal_request.confirmation = False
                withdrawal_request.confirmation_clicked = True
                withdrawal_request.save()
                return HttpResponse( 'Thanks for your confirmation. The withdrawal request is cancelled. Expect refund.')
        else:
            return HttpResponse('You have confirmed this withdrawal request before.')
    elif type == 'p_c_c_f':
        withdrawal_request = WithdrawProjectFunds.objects.get(pk=withdrawal_pk)
        if not withdrawal_request.confirmation_clicked:
            if response == 'yes':
                withdrawal_request.confirmation = True
                withdrawal_request.confirmation_clicked = True
                withdrawal_request.save()

                Transaction.objects.create(
                owner=withdrawal_request.innovator,
                description= f"You made a withdrawal of ₦{withdrawal_request.amount} from {withdrawal_request.project.name}'s funds into {withdrawal_request.account_number}-{withdrawal_request.bank_name}",
                successful = not False,
                reference_code = withdrawal_request.reference_code,
                amount = withdrawal_request.amount,
                pre_balance=withdrawal_request.project.fund_raised,
                post_balance = withdrawal_request.project.fund_raised - withdrawal_request.amount,
                type = 'WITHDRAWAL',
            )
                return HttpResponse('Thanks for your confirmation. Payment will be made soon.')
            else:
                project = withdrawal_request.project
                project.fund_raised += withdrawal_request.amount
                project.save(update_fields=['fund_raised'])

                withdrawal_request.confirmation = False
                withdrawal_request.confirmation_clicked = True
                withdrawal_request.save()
                return HttpResponse( 'Thanks for your confirmation. The withdrawal request is be cancelled. Expect refund soon')
        else:
            return HttpResponse('You have confirmed this withdrawal request before.')
    return redirect('home')
    # return render(request, 'core/withdrawal-confirmation.html', context)

@login_required
def send_kbq(request, withdrawal_pk, type):
    if type == 'p_f':
        withdrawal_request = Withdrawal.objects.get(pk=withdrawal_pk)
        current_site = get_current_site(request)
        subject = 'Knowledge-Based Question Confirmation'
        html_message = loader.render_to_string(
            'core/kbq-confirmation-request.html', {
            'user': withdrawal_request.innovator.user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(withdrawal_request.innovator.user.pk)),
            'withdrawal_request': withdrawal_request,
            'kbq': KBAQuestion.objects.get(user__pk=withdrawal_request.innovator.user.pk),
            'type': 'p_f',
            'pk': withdrawal_pk
        }, request=request
        )
        to_email = f'{withdrawal_request.innovator.user.email}'
        send_mail(subject, message = strip_tags(html_message), from_email=from_email, recipient_list= [to_email], fail_silently=False, html_message=html_message)
        messages.success(request, 'Confirmation email has successfully been sent. ✅')
        return redirect('withdrawal_requests')
    elif type == 'p_c_c_f':
        withdrawal_request = WithdrawProjectFunds.objects.get(pk=withdrawal_pk)
        current_site = get_current_site(request)
        subject = 'Knowledge-Based Question Confirmation'
        html_message = loader.render_to_string(
            'core/kbq-confirmation-request.html', {
            'user': withdrawal_request.innovator.user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(withdrawal_request.innovator.user.pk)),
            'withdrawal_request': withdrawal_request,
            'kbq': KBAQuestion.objects.get(user__pk=withdrawal_request.innovator.user.pk),
            'type': 'p_c_c_f',
            'pk': withdrawal_pk
        }, request=request
        )
        to_email = f'{withdrawal_request.innovator.user.email}'
        send_mail(subject, message = strip_tags(html_message), from_email=from_email, recipient_list= [to_email], fail_silently=False, html_message=html_message)
        messages.success(request, 'Confirmation email has successfully been sent. ✅')
        return redirect('withdrawal_requests')
    return render(request, 'core/withdrawal-requests.html')

# @login_required
@csrf_exempt
def kbq_confirmation(request, withdrawal_pk, type):
    # withdrawal_pk = request.GET.get('withdrawal_pk')
    # type = request.GET.get('type')
    context = {}
    kbq_form = KBQForm()
    context['kbq_form'] = kbq_form
    if request.method == 'POST':
        kbq_form = KBQForm(request.POST)
        if kbq_form.is_valid():
            kbq_answer = kbq_form.cleaned_data.get('kbq_answer').lower()
            if type == 'p_f':
                withdrawal_request = Withdrawal.objects.get(pk=withdrawal_pk)
                withdrawal_request.kbq_answer = kbq_answer
                withdrawal_request.save(update_fields=['kbq_answer'])
                context['withdrawal_request'] = withdrawal_request

                user = withdrawal_request.innovator.user

                kbq = KBAQuestion.objects.get(user__pk=user.pk)
                context['kbq'] = kbq
                
                
                if kbq_answer == kbq.answer.lower():
                    withdrawal_request.kbq_answer_status = 'right'
                    withdrawal_request.save(update_fields=['kbq_answer_status'])
                    return HttpResponse('Correct, expect payment soon.')
                else:
                    withdrawal_request.kbq_answer_status = 'wrong'
                    withdrawal_request.save(update_fields=['kbq_answer_status'])
                    return HttpResponse('Wrong, your withdrawal request has been declined. Expect refund soon')
            elif type == 'p_c_c_f':
                withdrawal_request = WithdrawProjectFunds.objects.get(pk=withdrawal_pk)
                withdrawal_request.kbq_answer = kbq_answer
                withdrawal_request.save(update_fields=['kbq_answer'])
                context['withdrawal_request'] = withdrawal_request

                user = withdrawal_request.innovator.user
                
                kbq = KBAQuestion.objects.get(user__pk=user.pk)
                context['kbq'] = kbq
                
                if kbq_answer == kbq.answer.lower():
                    withdrawal_request.kbq_answer_status = 'right'
                    withdrawal_request.save(update_fields=['kbq_answer_status'])
                    return HttpResponse('Correct, expect payment soon.')
                else:
                    withdrawal_request.kbq_answer_status = 'wrong'
                    withdrawal_request.save(update_fields=['kbq_answer_status'])
                    return HttpResponse('Wrong, your withdrawal request has been declined. Expect refund soon')
            context['kbq_form'] = KBQForm(
                {
                    'kbq_answer': kbq_answer
                }
            )
            
    return render(request, 'core/kbq-confirmation-request.html', context)

@login_required
def approve_withdrawal_request(request, withdrawal_pk, type):
    context = {}
    if request.user.is_moderator:
        moderator = Moderator.objects.get(user__pk=request.user.pk)
        if type == 'p_f':
            withdrawal_request = Withdrawal.objects.get(pk=withdrawal_pk)
            withdrawal_request.approved_by = moderator
            withdrawal_request.withdrawal_status = 'APPROVED'
            withdrawal_request.is_approved = True
            withdrawal_request.date_approved = datetime.datetime.now()
            withdrawal_request.save(update_fields=['approved_by', 'withdrawal_status', 'is_approved'])
            context['approved_withdrawal_request'] = withdrawal_request

            current_site = get_current_site(request)
            subject = 'Update about your Withdrawal Request'
            html_message = loader.render_to_string(
                'core/withdrawal_request_status.html', {
                'user': withdrawal_request.innovator.user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(withdrawal_request.innovator.user.pk)),
                'withdrawal_request': withdrawal_request,
                'type': 'p_f',
                'status': 'APPROVED',
                'pk': withdrawal_pk
            }, request=request
            )
            to_email = f'{withdrawal_request.innovator.user.email}'
            send_mail(subject, message = strip_tags(html_message), from_email=from_email, recipient_list= [to_email], fail_silently=False, html_message=html_message)

            messages.success(request, 'Withdrawal request has been successfully approved')
            return redirect('withdrawal_requests')
        elif type == 'p_c_c_f':
            withdrawal_request = WithdrawProjectFunds.objects.get(pk=withdrawal_pk)
            withdrawal_request.approved_by = moderator
            withdrawal_request.withdrawal_status = 'APPROVED'
            withdrawal_request.is_approved = True
            withdrawal_request.date_approved = datetime.datetime.now()
            withdrawal_request.save(update_fields=['approved_by', 'withdrawal_status', 'is_approved'])
            context['approved_withdrawal_request'] = withdrawal_request

            current_site = get_current_site(request)
            subject = 'Update about your Withdrawal Request'
            html_message = loader.render_to_string(
                'core/withdrawal_request_status.html', {
                'user': withdrawal_request.innovator.user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(withdrawal_request.innovator.user.pk)),
                'withdrawal_request': withdrawal_request,
                'type': 'p_c_c_f',
                'status': 'APPROVED',
                'pk': withdrawal_pk
            }, request=request
            )
            to_email = f'{withdrawal_request.innovator.user.email}'
            send_mail(subject, message = strip_tags(html_message), from_email=from_email, recipient_list= [to_email], fail_silently=False, html_message=html_message)

            messages.success(request, 'Withdrawal request has been successfully approved')
            return redirect('withdrawal_requests')
    else:
        return HttpResponse('You do not have the privilege to view this page.')
    return render(request, 'core/withdrawal_requests.html', context)


@login_required
def reject_withdrawal_request(request, withdrawal_pk, type):
    context = {}
    if request.user.is_moderator:
        moderator = Moderator.objects.get(user__pk=request.user.pk)
        if type == 'p_f':
            withdrawal_request = Withdrawal.objects.get(pk=withdrawal_pk)
            withdrawal_request.approved_by = moderator
            withdrawal_request.withdrawal_status = 'REJECTED'
            withdrawal_request.is_approved = True
            withdrawal_request.date_approved = datetime.datetime.now()
            withdrawal_request.save(update_fields=['approved_by', 'withdrawal_status', 'is_approved'])
            context['approved_withdrawal_request'] = withdrawal_request

            current_site = get_current_site(request)
            subject = 'Update about your Withdrawal Request'
            html_message = loader.render_to_string(
                'core/withdrawal_request_status.html', {
                'user': withdrawal_request.innovator.user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(withdrawal_request.innovator.user.pk)),
                'withdrawal_request': withdrawal_request,
                'type': 'p_f',
                'status': 'REJECTED',
                'pk': withdrawal_pk
            }, request=request
            )
            to_email = f'{withdrawal_request.innovator.user.email}'
            send_mail(subject, message = strip_tags(html_message), from_email=from_email, recipient_list= [to_email], fail_silently=False, html_message=html_message)

            messages.success(request, 'Withdrawal request has been successfully rejected')
            return redirect('withdrawal_requests')
        elif type == 'p_c_c_f':
            withdrawal_request = WithdrawProjectFunds.objects.get(pk=withdrawal_pk)
            withdrawal_request.approved_by = moderator
            withdrawal_request.withdrawal_status = 'REJECTED'
            withdrawal_request.is_approved = True
            withdrawal_request.date_approved = datetime.datetime.now()
            withdrawal_request.save(update_fields=['approved_by', 'withdrawal_status', 'is_approved'])
            context['approved_withdrawal_request'] = withdrawal_request

            current_site = get_current_site(request)
            subject = 'Update about your Withdrawal Request'
            html_message = loader.render_to_string(
                'core/withdrawal_request_status.html', {
                'user': withdrawal_request.innovator.user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(withdrawal_request.innovator.user.pk)),
                'withdrawal_request': withdrawal_request,
                'type': 'p_c_c_f',
                'status': 'REJECTED',
                'pk': withdrawal_pk
            }, request=request
            )
            to_email = f'{withdrawal_request.innovator.user.email}'
            send_mail(subject, message = strip_tags(html_message), from_email=from_email, recipient_list= [to_email], fail_silently=False, html_message=html_message)

            messages.success(request, 'Withdrawal request has been successfully rejected')
            return redirect('withdrawal_requests')
    else:
        return HttpResponse('You do not have the privilege to view this page.')
    return render(request, 'core/withdrawal_requests.html', context)

@login_required
def approve_send_money_request(request, sender, recipient, amount_to_send, send_money_pk, contribution_pk=None):
    from .tasks import send_money_recipient_email_task
    send_money = SendMoney.objects.get(pk=send_money_pk)
    if send_money.is_approved == False:
        sender = Innovator.objects.get(user__username=sender)
        recipient = Innovator.objects.get(user__username=recipient)
        amount_to_send = int(amount_to_send)
        
        send_money.is_approved = True
        send_money.save(update_fields=['is_approved'])

        sender.account_balance -= amount_to_send
        sender.save(update_fields=['account_balance'])
        
        if recipient.account_balance == None:
            recipient.account_balance = 0
        recipient.account_balance += amount_to_send
        recipient.save(update_fields=['account_balance'])
        Transaction.objects.create(
            owner=sender,
            description= f"You sent ₦{amount_to_send} to {send_money.recipient.user.username} on {send_money.date}",
            successful = not False,
            reference_code = send_money.reference_code,
            amount = amount_to_send,
            pre_balance = sender.account_balance + amount_to_send,
            post_balance = sender.account_balance,
            type = 'OUTGOING TRANSFER'
        )
        send_money.create_receive_money_instance()
        send_money_recipient_email_task.apply_async(
            kwargs = {
                'send_money': send_money.pk
            },
            countdown = 10
        )
        if contribution_pk is not None:
            contribution = Contribution.objects.get(pk=contribution_pk)
            innovation = contribution.innovation
            innovation.reward_paid = True
            innovation.save(update_fields=['reward_paid'])
    else:
        return HttpResponseForbidden('You have already responded to this request')
    return HttpResponse(f'You have successfully sent ₦{amount_to_send} to {recipient}.')
    

@login_required
def reject_send_money_request(request, amount_to_send, recipient, send_money_pk):
    send_money = SendMoney.objects.get(pk=send_money_pk)
    if send_money.is_approved == False:
        recipient = Innovator.objects.get(user__username=recipient)
    else:
        return HttpResponseForbidden('You have already responded to this request')
    return HttpResponse(f'Your request to send  ₦{amount_to_send} to {recipient.user.username} failed due to disapproval from the owner of this account.')

@login_required
def add_milestone(request, project_pk):
    from .tasks import send_milestone_email_task
    context = {}
    project = Project.objects.get(pk=project_pk)
    add_milestone_form_errors = None
    context['project'] = project
    if request.user.username == project.innovator.user.username:
        add_milestone_form = AddMilestoneForm()
        context['add_milestone_form'] = add_milestone_form
        if request.method == 'POST':
            add_milestone_form = AddMilestoneForm(request.POST or None, request.FILES or None)
            context['add_milestone_form'] = add_milestone_form
            add_milestone_form_errors = add_milestone_form
            if add_milestone_form.is_valid():
                add_milestone_form_obj = add_milestone_form.save(commit=False)
                add_milestone_form_obj.project = project
                add_milestone_form.save()
                milestone = ProjectMilestone.objects.filter(project__pk=project_pk).latest('date_added')
                current_site = get_current_site(request)

                # SENDS EMAIL TO EVERY INVESTOR ABOUT THE ADDITION OF A NEW MILESTONE
                send_milestone_email_task.apply_async(
                    kwargs = {
                        'investment_pk': project_pk,
                        'milestone_pk': milestone.pk,
                        'current_site': current_site.domain,
                        'type': 'new'
                    },
                    countdown = 10
                )

                messages.success(request, 'Milestone added successfully.')
                return redirect('project_details', project_pk)

            else:
                print(add_milestone_form.errors.as_data())
    else:
        return HttpResponse('You do not have the privilege to access this page')
    return render(request, 'core/add-milestone.html', context)

@login_required
def project_milestones(request, project_pk):
    context = {}
    project = Project.objects.get(pk=project_pk)
    project_milestones = ProjectMilestone.objects.filter(project__pk=project_pk)
    context['project_milestones'] = project_milestones
    return render(request, 'core/project-milestones.html', context)

@login_required
def milestone_detail(request, milestone_pk):
    context = {}
    milestone = ProjectMilestone.objects.get(pk=milestone_pk)
    context['milestone'] = milestone
    return render(request, 'core/milestone-detail.html', context)

@login_required
def update_milestone(request, milestone_pk):
    from .tasks import send_milestone_email_task
    context = {}
    milestone = ProjectMilestone.objects.get(pk=milestone_pk)
    context['milestone'] = milestone
    if request.method == 'POST':
        update_milestone_details_form_data = {
            'status': request.POST.get('status'),
        }
        update_milestone_details_form = UpdateMilestoneDetailsForm(update_milestone_details_form_data, instance=milestone)
        if update_milestone_details_form.is_valid():
            # milestone_obj = update_milestone_details_form.save(commit=False)
            milestone.date_updated = datetime.datetime.now()
            milestone.save()
            update_milestone_details_form.save()
            current_site = get_current_site(request)

            # SENDS EMAIL TO EVERY INVESTOR ABOUT THE UPDATE OF THE MILESTONE
            send_milestone_email_task.apply_async(
                kwargs= {
                    'investment_pk': milestone.project.pk,
                    'current_site': current_site.domain,
                    'milestone_pk': milestone.pk,
                    'type': 'updated'
                },
                countdown=10
            )

            messages.success(request, 'Milestone has been updated!')
            return redirect('milestone_details', milestone.pk)
    else:
        update_milestone_details_form = UpdateMilestoneDetailsForm(
            instance=milestone, initial= {
                'title': milestone.title,
                'description': milestone.description,
                # 'target_date': milestone.target_date,
                'progress_report': milestone.progress_report,
                'image_1': milestone.image_1,
                'image_2': milestone.image_2,
                'image_3': milestone.image_3,
                'video': milestone.video,
                'date_added': milestone.date_added,
                'status': milestone.status,
            }
        )
    context['update_milestone_details_form'] = update_milestone_details_form
    return render(request, 'core/update-milestone-details.html', context)

def pagination(request, object, num_of_pages):
    # request.session['query'] = query
    page_number = request.GET.get('page', 1)
    objects_paginator = Paginator(object, num_of_pages)
    try:
        objects = objects_paginator.page(page_number)
    except PageNotAnInteger:
        objects = objects_paginator.page(1)
    except EmptyPage:
        objects = objects_paginator.page(objects_paginator.num_pages)
    return objects


def search_innovations(request):
    context = {}
    query = request.GET.get('query')
    request.session['innovation_query'] = query
    context['query'] = query
    if request.method == 'GET':
        if query:
            innovations = Innovation.objects.filter(
                Q(title__icontains=query) | Q(description__icontains=query)
            ).order_by('-date_created').distinct()
            # if not innovations:
            #     request.session['search_innovations_no_result'] = True
            #     return redirect('innovations_list')
            innovations = pagination(request, innovations, 4)
            context['innovations'] = innovations
            request.session['search_innovations_no_result'] = False
        else:
            innovations = pagination(request, Innovation.objects.all().order_by('-date_created'), 4)
            context['innovations'] = innovations
    return render(request, 'core/innovations-list.html', context)


def send_funding_completed_email(investment_pk):
    investment = Project.objects.get(pk=investment_pk)

    # FOR PROJECT OWNER
    investment_owner = investment.innovator
    subject = f'Hurray {investment_owner.user.get_full_name()}, Your Investment Project "{investment.name}" Has Successfully Reached Its Funding Goal. 🎉🍾'
    html_message = loader.render_to_string(
        'core/fund_raising_completed.html', {
            'user': investment_owner.user,
            'investment_project': investment,
            'date': datetime.datetime.now()

        }
    )
    to_email = [f'{investment_owner.user.email}']
    send_mail(
        subject=subject,
        message=strip_tags(html_message),
        from_email=from_email,
        recipient_list=to_email,
        fail_silently=False,
        html_message=html_message
    )


    # FOR INVESTORS
    recipients = Make_Investment.objects.filter(investment=investment)
    members = Group.objects.get(investment_project=investment).get_group_members
    for recipient in members:
        subject = f'Hurray {recipient.get_full_name()}, An Investment Project Named "{investment.name}" That You Invested In Has Successfully Reached Its Funding Goal. 🎉🍾'
        html_message = loader.render_to_string(
            'core/fund_raising_completed_investors.html', {
                'user': recipient,
                'investment_project': investment,
                'date': datetime.datetime.now()

            }
        )
        to_email = [f'{recipient.email}']
        send_mail(
            subject=subject,
            message=strip_tags(html_message),
            from_email=from_email,
            recipient_list=to_email,
            fail_silently=False,
            html_message=html_message
        )


def send_milestone_email(investment_pk, current_site, milestone_pk, type):
    investment = Project.objects.get(pk=investment_pk)
    investors = Make_Investment.objects.filter(investment__pk=investment_pk).values_list('sender', flat=True).distinct()
    milestone = ProjectMilestone.objects.get(pk=milestone_pk)

    if type.lower() == 'new':
        subject = f'Update: New Milestone Added to "{milestone.project.name}" Investment Project by the project owner'
        for investor in investors:
            investor = Innovator.objects.get(pk=investor)
            html_message = loader.render_to_string(
                'core/send-milestone-addition-notification.html', {
                'user': investor.user,
                'domain': current_site,
                'project': investment,
                'milestone_title': milestone.title,
                'milestone': milestone,
            }
            )
            to_email = f'{investor.user.email}'
            send_mail(subject, message = strip_tags(html_message), from_email=from_email, recipient_list= [to_email], fail_silently=False, html_message=html_message)

    elif type.lower() == 'updated':
        subject = f'Update: "{milestone.title}" Milestone of the project "{milestone.project.name}" was updated by the project owner'
        for investor in investors:
            investor = Innovator.objects.get(pk=investor)
            html_message = loader.render_to_string(
                'core/send-milestone-update-notification.html', {
                'user': investor.user,
                'domain': current_site,
                'milestone': milestone,
            },
            )
            to_email = f'{investor.user.email}'
            send_mail(subject, message = strip_tags(html_message), from_email=from_email, recipient_list= [to_email], fail_silently=False, html_message=html_message)


def send_project_approval_status(investment_pk):
    investment = Project.objects.get(pk=investment_pk)
    to_email = [f"{investment.innovator.user.email}"]
    subject = f'Hello, {investment.innovator.user.username}.There is an update about an Investment Project you submitted recently.'
    html_message = loader.render_to_string(
        'core/send-project-approval_status.html', {
        'user': investment.innovator.user,
        'project': investment
    }
    )
    send_mail(subject, message=strip_tags(html_message), from_email=from_email, recipient_list=to_email, fail_silently=False, html_message=html_message)

def pay_investors(investment_pk):
    project = Project.objects.get(pk=investment_pk)
    project_owner = project.innovator
    
    investments_made = Make_Investment.objects.filter(investment=project)

    for investment in investments_made:
        investor = investment.sender

        # FOR PROJECT OWNER
        project_owner_transaction = Transaction.objects.create(
            owner = project_owner,
            description = f'You sent ₦{investment.expected_return} to {investment.sender.user.get_full_name} as their ROI on their investment of  ₦{investment.amount} in {investment.investment.name} project.',
            successful = True,
            amount = investment.expected_return,
            pre_balance = project_owner.account_balance,
            post_balance = project_owner.account_balance - investment.expected_return,
            type = 'OUTGOING - PAYMENT OF ROI')
        project_owner.account_balance -= investment.expected_return
        project_owner.save(update_fields=['account_balance'])

        # EMAIL FOR PROJECT SENDER
        subject = f'You made payment of ROI(return of investment) to {investment.sender.user.get_full_name()}.'
        to_email = [f'{project_owner.user.email}']
        user = project_owner.user
        html_message = loader.render_to_string(
            'core/project-owner-roi-payment.html',{
                'user': user,
                'amount_paid': investment.expected_return,
                'recipient': investor.user,
                'date': project_owner_transaction.date_generated,
                'project': project,
                'investment': investment
            }
        )
        # subject = f'You made payment of ROI(return of investment) of ₦{investment.expected_return} to {investment.sender.user.get_full_name} on {project_owner_transaction.date_generated}'

        send_mail(subject, message=strip_tags(html_message), recipient_list=to_email, fail_silently=False, html_message=html_message, from_email=from_email)



        # FOR INVESTOR
        investor_transaction = Transaction.objects.create(
            owner = investor,
            description = f'You received ₦{investment.expected_return} from {investment.investment.innovator.user.get_full_name()} as your ROI(return of investment) on "{investment.investment.name}" investment project that you invested in on {investment.date_sent}.',
            successful = True,
            amount = investment.expected_return,
            pre_balance = investor.account_balance,
            post_balance = investor.account_balance + investment.expected_return,
            type = 'INCOMING - PAYMENT OF ROI',
            reference_code = project_owner_transaction.reference_code
        )
        investor.account_balance += investment.expected_return
        investor.save(update_fields=['account_balance'])
        # EMAIL FOR INVESTOR
        subject = f'You received ₦{investment.expected_return} from {project_owner.user.get_full_name()} as payment of ROI(return of investment) on {investment.investment.name} investment project.'
        to_email = [f'{investor.user.email}']
        user = investor.user
        html_message = loader.render_to_string(
            'core/investor-roi-payment.html',{
                'user': user,
                'amount_received': investment.expected_return,
                'sender': project_owner.user,
                'date': investor_transaction.date_generated,
                'investment': investment
            }
        )

        send_mail(subject, message=strip_tags(html_message), recipient_list=to_email, fail_silently=False, html_message=html_message, from_email=from_email)

        project.completed = True
        project.save(update_fields=['completed'])
    # return HttpResponse('Payment of all ROIs is being processed.')


@login_required
def payment_of_roi(request, investment_pk):
    project = Project.objects.get(pk=investment_pk)
    from .tasks import pay_investors_task

    if request.user != project.innovator.user:
        return HttpResponse('You are not the project owner.')
    
    if not project.completed:
        total_amount_to_pay = 0
        
        investments_made = Make_Investment.objects.filter(investment=project)

        for investment in investments_made:
            total_amount_to_pay += investment.expected_return

        if project.innovator.account_balance < total_amount_to_pay:
            amount_remaining = total_amount_to_pay - project.innovator.account_balance
            return HttpResponse(f'Insufficent Funds. Deposit ₦{amount_remaining} more in order to be able to pay all investors.')

        pay_investors_task.apply_async(
            kwargs= {
                'investment_pk': investment_pk
            },
            countdown=10
        )
        messages.success(request, 'Your request to pay all investors of this project is being processed!')
        return redirect('investment_capital')
    else:
        return HttpResponse('This investment project has been completed')
    
def send_money_recipient_email(send_money_pk):
    send_money = SendMoney.objects.get(pk=send_money_pk)
    to_email = [f"{send_money.recipient.user.email}"]
    subject = f"{send_money.sender.user.get_full_name()} sent you some funds."
    html_message = loader.render_to_string(
        'core/send_money_recipient_email.html', {
            'user': send_money.recipient.user,
            'amount': send_money.amount,
            'sender': send_money.sender.user.get_full_name(),
            'recipient': send_money.recipient,
            'date':send_money.date
        }
    )
    send_mail(subject, message=strip_tags(html_message), recipient_list=to_email, from_email=from_email, fail_silently=False, html_message=html_message)

def send_money_2(amount_to_send, sender_pk, recipient_pk, sender_prebalance, sender_postbalance, domain):
    sender = Innovator.objects.get(pk=sender_pk)
    recipient = Innovator.objects.get(pk=recipient_pk)

    send_money = SendMoney.objects.create(
    amount = amount_to_send,
    sender = sender,
    recipient = recipient,
    pre_balance = sender_prebalance,
    post_balance = sender_postbalance,
    is_approved = False
    )

    subject = 'Funds Transfer Confirmation'
    html_message = loader.render_to_string(
    'core/confirm_nin.html', {
    'user': sender.user,
    'domain': domain,
    'amount': int(amount_to_send),
    'date': datetime.datetime.now(),
    'sender': sender,
    'recipient': recipient,
    'amount_to_send': amount_to_send,
    'send_money_pk': send_money.pk
    }
    )
    to_email = f'{sender.user.email}'
    send_mail(subject, message = strip_tags(html_message), from_email=from_email, recipient_list= [to_email], fail_silently=False, html_message=html_message)

def notify_investors_of_project_fund_withdrawal(withdrawal_pk):
    withdrawal_request = WithdrawProjectFunds.objects.get(pk=withdrawal_pk)
    investors_emails = Make_Investment.objects.filter(investment=withdrawal_request.project).values_list('sender__user__email', flat=True).distinct()

    subject = "The Project Manager of An Investment Project You Invested Has Requested For Withdrawal of the Project Funds"
    
    html_message = loader.render_to_string(
        'core/notify_investors_of_project_fund_withdrawal.html', {
            'project_manager_name': withdrawal_request.project.innovator.user.get_full_name(),
            'amount_requested': withdrawal_request.amount,
            'date_requested': withdrawal_request.date,
            'project_name': withdrawal_request.project.name
        }
    )

    send_mail(subject, message=strip_tags(html_message), recipient_list=investors_emails, fail_silently=False, from_email=from_email, html_message=html_message)