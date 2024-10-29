from django import forms
from .models import ParkingImage, Vehicle, ParkingSession, UserProfile, ParkingSpot
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone


class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    monetary_limit = forms.DecimalField(max_digits=10, decimal_places=2, required=True)

    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'monetary_limit']

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].initial = self.instance.user.first_name
        self.fields['last_name'].initial = self.instance.user.last_name

    def save(self, commit=True):
        user_profile = super(UserProfileForm, self).save(commit=False)
        user_profile.user.first_name = self.cleaned_data['first_name']
        user_profile.user.last_name = self.cleaned_data['last_name']
        if commit:
            user_profile.user.save()
            user_profile.save()
        return user_profile


class TransactionForm(forms.Form):
    vehicle = forms.ModelChoiceField(queryset=Vehicle.objects.none(), label="Vehicle")
    start_date = forms.DateField(label="Start Date", widget=forms.DateInput(attrs={'type': 'date'}))
    parking_spot = forms.ModelChoiceField(queryset=ParkingSpot.objects.none(), required=False, label="Parking Spot")

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            self.fields['vehicle'].queryset = Vehicle.objects.filter(owner=user, is_blocked=False)

        now = timezone.now()
        occupied_spots = Vehicle.objects.filter(
            parking_spot__isnull=False,
            subscription_end_date__gte=now
        ).values_list('parking_spot', flat=True)

        self.fields['parking_spot'].queryset = ParkingSpot.objects.filter(
            spot_type='SUBSCRIPTION',
            is_occupied=False
        ).exclude(id__in=occupied_spots)


class ParkingImageForm(forms.ModelForm):
    class Meta:
        model = ParkingImage
        fields = ['image']


class UserRegisterForm(UserCreationForm):
    username = forms.CharField(max_length=50,
                               required=True,
                               widget=forms.TextInput(attrs={"class": "form-control"}))
    email = forms.EmailField(required=True,
                             widget=forms.EmailInput(attrs={"class": "form-control"}))

    password1 = forms.CharField(max_length=150,
                                required=True,
                                widget=forms.PasswordInput(attrs={"class": "form-control"}))
    password2 = forms.CharField(max_length=150,
                                required=True,
                                widget=forms.PasswordInput(attrs={"class": "form-control"}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['license_plate', 'vehicle_type']


class VehicleSearchForm(forms.Form):
    license_plate = forms.CharField(max_length=12, label='License Plate')

    def clean_license_plate(self):
        license_plate = self.cleaned_data['license_plate']
        cleaned_license_plate = license_plate.upper().replace(" ", "").replace("-", "")
        return cleaned_license_plate


class StartParkingSessionForm(forms.Form):
    vehicle = forms.ModelChoiceField(
        queryset=Vehicle.objects.none(),  # Initially empty, will be populated in __init__
        label="Vehicle"
    )
    entry_time = forms.DateTimeField(
        label="Entry Time",
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')  
        super().__init__(*args, **kwargs)

        if user.is_superuser:
            self.fields['vehicle'].queryset = Vehicle.objects.all()
        else:
            self.fields['vehicle'].queryset = Vehicle.objects.filter(
                owner=user,
                is_blocked=False
            )


class EndParkingSessionForm(forms.Form):
    vehicle = forms.ModelChoiceField(
        queryset=Vehicle.objects.none(), 
        label="Vehicle"
    )
    exit_time = forms.DateTimeField(
        label="Exit Time",
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

        if user.is_superuser:
            self.fields['vehicle'].queryset = Vehicle.objects.filter(
                id__in=ParkingSession.objects.filter(exit_time__isnull=True).values('vehicle_id')
            ).distinct()
        else:
            self.fields['vehicle'].queryset = Vehicle.objects.filter(
                owner=user,
                id__in=ParkingSession.objects.filter(exit_time__isnull=True).values('vehicle_id')
            ).distinct()


class StartParkingSessionImageForm(forms.Form):
    image = forms.ImageField(label="Upload Image")
    entry_time = forms.DateTimeField(
        label="Entry Time",
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
    )


class EndParkingSessionImageForm(forms.Form):
    exit_time = forms.DateTimeField(
        label="Exit Time",
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
    )

