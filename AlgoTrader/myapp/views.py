# myapp/views.py

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.http import require_POST
from .models import Trade
import json
from AngelOne.db import get_stocks

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        username = 'ansh'
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/home/')
        else:
            return JsonResponse({'success': False, 'message': 'Invalid credentials'}, status=401)

    return render(request, 'myapp/login.html')

def logout_view(request):
    logout(request)
    return redirect('/')

@login_required(login_url='/') 
def home(request):
    trades = Trade.objects.all()
    return render(request, 'myapp/home.html', {'trades': trades})

@login_required(login_url='/')
def new(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            stock1 = data.get('stock1')
            stock2 = data.get('stock2')
            quantity = int(data.get('quantity'))
            entry = float(data.get('entry'))
            entry_diff = data.get('entryDiff')
            exit = float(data.get('exit'))
            exit_diff = data.get('exitDiff')
            stop_loss = float(data.get('stopLoss'))
            stop_loss_diff = data.get('stopLossDiff')

            # Create a new Trade object and save it to the database
            trade = Trade(
                stock1=stock1,
                stock2=stock2,
                quantity=quantity,
                entry=entry,
                entry_diff=entry_diff,
                exit=exit,
                exit_diff=exit_diff,
                stop_loss=stop_loss,
                stop_loss_diff=stop_loss_diff
            )
            trade.save()

            return  JsonResponse({'success': True, 'message': 'Trade saved successfully!'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)
    else:
        # Fetch all stock options
        stocks = get_stocks()
        stock_symbols = [stock[0] for stock in stocks]
        return render(request, 'myapp/new.html', {'stock_symbols': stock_symbols})

@login_required(login_url='/') 
def edit(request, id): 
    if request.method == 'POST':
        data = json.loads(request.body)
        try:
            trade = Trade.objects.get(id=id)
            trade.stock1 = data.get('stock1')
            trade.stock2 = data.get('stock2')
            trade.quantity = int(data.get('quantity'))
            trade.entry = float(data.get('entry'))
            trade.entry_diff = data.get('entryDiff')
            trade.exit = float(data.get('exit'))
            trade.exit_diff = data.get('exitDiff')
            trade.stop_loss = float(data.get('stopLoss'))
            trade.stop_loss_diff = data.get('stopLossDiff')
            trade.save()
            return JsonResponse({'success': True, 'message': 'Trade updated successfully'})
        except Trade.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Trade not found'}) 
    else:
        # Fetch the trade object or return a 404 if not found
        trade = get_object_or_404(Trade, id=id)

        # Fetch all stock options
        stocks = get_stocks()
        stock_symbols = [stock[0] for stock in stocks]

        # Pass the trade object with all stock symbols to the template
        context = {
            'trade': trade,
            'stock_symbols': stock_symbols
        }
        
        return render(request, 'myapp/edit.html', context)

@login_required(login_url='/')
@require_POST
def delete(request, id):
    try:
        trade = Trade.objects.get(id=id)
        trade.delete()
        return JsonResponse({'success': True, 'message': 'Trade deleted successfully'})
    except Trade.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Trade not found'}) 