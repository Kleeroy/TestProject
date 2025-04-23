

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count, Q
from django.utils import timezone
import json

from .models import Member, Event, Attendance
from .forms import UserRegistrationForm, EventForm, DateRangeForm
from .utils import generate_qr_code, decrypt_data

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            member = Member.objects.create(
                user=user,
                student_id=form.cleaned_data['student_id'],
                section=form.cleaned_data['section']
            )
            login(request, user)
            return redirect('member_home')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})

@login_required
def home(request):
    try:
        member = Member.objects.get(user=request.user)
        if member.is_admin:
            return redirect('admin_home')
        else:
            return redirect('member_home')
    except Member.DoesNotExist:
        messages.error(request, 'Member profile not found.')
        return redirect('login')

def redirect_after_login(request):
    if request.user.is_superuser:
        return redirect('admin_home')
    else:
        # For regular members
        return redirect('member_home')

@login_required
def admin_home(request):
    member = get_object_or_404(Member, user=request.user)
    if not member.is_admin:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('member_home')
    
    # Summary stats
    total_members = Member.objects.filter(is_admin=False).count()
    active_events = Event.objects.filter(is_active=True).count()
    total_attendance = Attendance.objects.count()
    
    # Recent events
    recent_events = Event.objects.order_by('-date')[:5]
    
    context = {
        'member': member,
        'total_members': total_members,
        'active_events': active_events,
        'total_attendance': total_attendance,
        'recent_events': recent_events,
    }
    
    return render(request, 'admin/home.html', context)

@login_required
def member_home(request):
    member = get_object_or_404(Member, user=request.user)
    if member.is_admin:
        return redirect('admin_home')
    
    # Get attendance statistics
    total_events = Event.objects.count()
    attended_events = Attendance.objects.filter(member=member).count()
    attendance_rate = (attended_events / total_events * 100) if total_events > 0 else 0
    
    # Get recent attendance history
    recent_attendance = Attendance.objects.filter(member=member).order_by('-timestamp')[:5]
    
    # Generate QR code
    qr_code_image = generate_qr_code(member)
    
    context = {
        'member': member,
        'total_events': total_events,
        'attended_events': attended_events,
        'missed_events': total_events - attended_events,
        'attendance_rate': round(attendance_rate, 2),
        'recent_attendance': recent_attendance,
        'qr_code_image': qr_code_image,
    }
    
    return render(request, 'member/home.html', context)

@login_required
def member_qr_code(request):
    member = get_object_or_404(Member, user=request.user)
    qr_code_image = generate_qr_code(member)
    
    context = {
        'member': member,
        'qr_code_image': qr_code_image,
    }
    
    return render(request, 'member/qr_code.html', context)

@login_required
def member_attendance_stats(request):
    member = get_object_or_404(Member, user=request.user)
    
    # Get all events
    events = Event.objects.all().order_by('-date')
    
    # Get attendance for this member
    attendance = Attendance.objects.filter(member=member)
    attended_event_ids = [a.event_id for a in attendance]
    
    # Mark events as attended or not
    for event in events:
        event.attended = event.id in attended_event_ids
    
    # Calculate statistics
    total_events = events.count()
    attended_count = attendance.count()
    missed_count = total_events - attended_count
    attendance_rate = (attended_count / total_events * 100) if total_events > 0 else 0
    
    context = {
        'member': member,
        'events': events,
        'total_events': total_events,
        'attended_count': attended_count,
        'missed_count': missed_count,
        'attendance_rate': round(attendance_rate, 2),
    }
    
    return render(request, 'member/attendance_stats.html', context)

@login_required
def create_event(request):
    member = get_object_or_404(Member, user=request.user)
    if not member.is_admin:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('member_home')
    
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = member
            event.save()
            messages.success(request, 'Event created successfully.')
            return redirect('event_attendees', event_id=event.id)
    else:
        form = EventForm()
    
    context = {
        'form': form,
        'member': member,
    }
    
    return render(request, 'admin/create_event.html', context)

@login_required
def event_attendees(request, event_id):
    member = get_object_or_404(Member, user=request.user)
    if not member.is_admin:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('member_home')
    
    event = get_object_or_404(Event, id=event_id)
    attendees = Attendance.objects.filter(event=event).order_by('timestamp')
    
    context = {
        'member': member,
        'event': event,
        'attendees': attendees,
    }
    
    return render(request, 'admin/event_attendees.html', context)

@login_required
@csrf_exempt
def scan_qr_code(request, event_id):
    """API endpoint for processing QR code scans"""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
    
    # Check if user is admin
    member = get_object_or_404(Member, user=request.user)
    if not member.is_admin:
        return JsonResponse({'status': 'error', 'message': 'Access denied'}, status=403)
    
    # Get event
    event = get_object_or_404(Event, id=event_id)
    if not event.is_active:
        return JsonResponse({'status': 'error', 'message': 'Event is not active'}, status=400)
    
    # Decode QR code data
    try:
        data = json.loads(request.body)
        encrypted_data = json.loads(data.get('qr_data', '{}'))
        
        # Decrypt the data
        member_data = decrypt_data(encrypted_data)
        
        # Find the member
        try:
            scanned_member = Member.objects.get(student_id=member_data['id'])
            
            # Check if already marked attendance
            attendance, created = Attendance.objects.get_or_create(
                member=scanned_member,
                event=event,
                defaults={'timestamp': timezone.now()}
            )
            
            if created:
                return JsonResponse({
                    'status': 'success',
                    'message': 'Attendance marked',
                    'member': {
                        'id': scanned_member.student_id,
                        'name': scanned_member.full_name,
                        'section': scanned_member.section
                    }
                })
            else:
                return JsonResponse({
                    'status': 'info',
                    'message': 'Attendance already marked',
                    'member': {
                        'id': scanned_member.student_id,
                        'name': scanned_member.full_name,
                        'section': scanned_member.section
                    }
                })
            
        except Member.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Member not found'}, status=404)
            
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Error processing QR code: {str(e)}'}, status=400)

@login_required
def admin_reports(request):
    member = get_object_or_404(Member, user=request.user)
    if not member.is_admin:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('member_home')
    
    # Get filter parameters
    form = DateRangeForm(request.GET or None)
    
    # Default to last 30 days if no filter
    if form.is_valid():
        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date']
    else:
        end_date = timezone.now().date()
        start_date = end_date - timezone.timedelta(days=30)
        form = DateRangeForm(initial={'start_date': start_date, 'end_date': end_date})
    
    # Get events within date range
    events = Event.objects.filter(date__range=[start_date, end_date]).order_by('-date')
    
    # Calculate attendance stats
    total_members = Member.objects.filter(is_admin=False).count()
    
    # Event attendance stats
    event_stats = []
    for event in events:
        attendees = Attendance.objects.filter(event=event).count()
        attendance_rate = (attendees / total_members * 100) if total_members > 0 else 0
        event_stats.append({
            'event': event,
            'attendees': attendees,
            'total_members': total_members,
            'attendance_rate': round(attendance_rate, 2)
        })
    
    # Member attendance stats
    members = Member.objects.filter(is_admin=False)
    member_stats = []
    for m in members:
        attended = Attendance.objects.filter(
            member=m,
            event__in=events
        ).count()
        
        attendance_rate = (attended / events.count() * 100) if events.count() > 0 else 0
        member_stats.append({
            'member': m,
            'attended': attended,
            'total_events': events.count(),
            'missed': events.count() - attended,
            'attendance_rate': round(attendance_rate, 2)
        })
    
    # Sort by attendance rate descending
    member_stats.sort(key=lambda x: x['attendance_rate'], reverse=True)
    
    context = {
        'member': member,
        'form': form,
        'events': events,
        'event_stats': event_stats,
        'member_stats': member_stats,
        'total_events': events.count(),
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'admin/reports.html', context)