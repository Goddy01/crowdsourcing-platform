from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from .models import Project, Innovation, Contribution, Reward_Payment, Investment_Payment
from django_countries import countries
from .forms import CreateProjectForm, CreateInnovationForm, MakeContributionForm
from accounts.models import Innovator, Moderator
from django.utils import timezone
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
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
            if create_project_form.cleaned_data['innovator_user_agreement']:
                project_obj.innovator_user_agreement = True
            project_obj.save()
            print('TIME: ', project_obj.date_created)
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
    print('ON RE: ', request.META.get('HTTP_REFERER'))
    if request.GET.get('from_expected_return'):
        from_expected_return = request.GET.get('from_expected_return')
        request.session['from_expected_return'] = from_expected_return
        to_expected_return = request.GET.get('to_expected_return')
        request.session['to_expected_return'] = to_expected_return

        if from_expected_return:
            print('FROM: ', from_expected_return)
            if to_expected_return:
                print('TO: ', to_expected_return)
                projects = Project.objects.filter(
                    Q(expected_return__range=(int(from_expected_return), int(to_expected_return)))
                )
                # projects = pagination(request, projects, 4)
            else:
                projects = Project.objects.filter(
                    Q(expected_return__gte=int(from_expected_return))
                )
                # projects = pagination(request, projects, 4)
    else:
        # request.GET
        projects = Project.objects.all()
    projects = pagination(request, projects, 4)
    return render(request, 'core/projects.html', {'projects': projects, "from_expected_return": request.GET.get('from_expected_return'), "to_expected_return": request.GET.get('to_expected_return')})

def project_details(request, project_pk):
    context = {}
    project = Project.objects.get(pk=project_pk)
    context['project'] = project
    # if not request.user.is_authenticated:
    #     return redirect('accounts:innovator_login')
    try:
        if request.user.is_innovator:
            investor_1 = Innovator.objects.get(user__pk=request.user.pk)
            context['investor_1'] = investor_1
        else:
            moderator = Moderator.objects.get(user__pk=request.user.pk)
            context['moderator'] = moderator
            print('YO: ', request.POST.get('status'))
            if request.method == 'POST'and 'status' in request.POST:
                project.status = request.POST.get('status')
                project.save()
                print('broo: ', project.status)
                
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
    print('ALL: ', contribution.upvoted_by.all())

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
def make_investment_payment(request, investment_pk):
    context = {}
    investment = Project.objects.get(pk=investment_pk)
    # if request.POST.get('bool') == 'True':
    if request.method == 'POST' and 'pay' in request.POST:
        make_payment = Investment_Payment.objects.create(
            send_to = Innovator.objects.get(user__email=investment.innovator.user.email),
            send_from = Innovator.objects.get(user__pk=request.user.pk),
            sender = Innovator.objects.get(user__pk=request.user.pk),
            amount = request.POST.get('amount'),
            investment = Project.objects.get(pk=investment_pk)
        )
        request.session['pk'] = investment.pk
        investment.target -= int(make_payment.amount)
        if investment.fund_raised is None:
            investment.fund_raised = 0
        investment.fund_raised += int(make_payment.amount)
        if investment.amount_left is None:
            investment.amount_left = investment.target
        investment.amount_left -= int(make_payment.amount)
        investment.save()
        context['make_payment'] = make_payment
        # return HttpResponse('Your payment is being proceesed!')
        return redirect('projects')
    # else:
    #     return HttpResponse('Your payment could not be authenticated')
    context['investment'] = investment
    return render(request, 'core/project_details.html', context)

@login_required
def invest(request, investment_pk):
    context = {}
    investment = Project.objects.get(pk=investment_pk)
    investor = Innovator.objects.get(user__pk=request.user.pk)
    investment_owner = investment.innovator
    context['investment'] = investment
    if request.method == 'POST' and 'invest' in request.POST:
        amount = int(request.POST.get('amount'))
        if amount <= investor.account_balance:
            investor.account_balance -= amount
            investment.target -= amount
            investor.save()
            if investment_owner.account_balance is None:
                investment_owner.account_balance = 0
            investment_owner.account_balance += amount
            investment_owner.save()
            if investment.fund_raised is None:
                investment.fund_raised = 0
            investment.fund_raised += amount
            if investment.amount_left == 0 and investment.fund_raised:
                investment.complete = True
            investment.save()
            messages.success(request, 'Thank you for investing in this project!')
            return redirect('project_details', investment_pk)
        else:
            return HttpResponse('Insufficient Account Balance ')

    return render(request, 'core/project_details.html', context)

@login_required
def investors(request, investment_pk):
    context = {}
    investors = Investment_Payment.objects.get(investment_pk=investment_pk).sender
    context['investors'] = investors
    return render(request, 'core/investment-investors.html', context)

@login_required
def investments(request):
    investments = Project.objects.filter(innovator__user__pk=request.user.pk)
    return render(request, 'core/investments.html', {'investments': investments})