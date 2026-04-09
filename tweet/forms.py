from django import forms
from .models import Tweet, Comment
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
MAX_IMAGE_SIZE_MB = 5


class TweetForm(forms.ModelForm):
    """Form for creating and editing tweets. The photo field is a plain
    FileField so that views can pass the file to Supabase Storage and store
    the returned public URL in photo_url rather than writing to disk."""

    photo = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control form-control-custom',
            'accept': 'image/jpeg,image/png,image/webp,image/gif',
            'id': 'id_photo',
            'aria-label': 'Attach an image (optional)',
        }),
        help_text='JPEG, PNG, WebP or GIF — max 5 MB',
    )

    class Meta:
        model = Tweet
        # photo_url is NOT exposed in the form; it's set programmatically by the view.
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control form-control-custom',
                'placeholder': "What's happening?",
                'rows': 4,
                'maxlength': '240',
                'id': 'id_text',
                'aria-label': 'Tweet content',
                'aria-describedby': 'char-counter',
            }),
        }

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if photo:
            if photo.size > MAX_IMAGE_SIZE_MB * 1024 * 1024:
                raise forms.ValidationError(
                    f'File too large. Maximum size is {MAX_IMAGE_SIZE_MB} MB.'
                )
            if photo.content_type not in ALLOWED_IMAGE_TYPES:
                raise forms.ValidationError(
                    'Unsupported file type. Please upload a JPEG, PNG, WebP, or GIF image.'
                )
        return photo


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control form-control-custom',
                'placeholder': field.label,
            })
            if field.help_text and 'password' in field_name.lower():
                field.help_text = 'Standard password requirements apply.'

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.TextInput(attrs={
                'placeholder': 'Add a comment...',
                'class': 'form-control form-control-sm form-control-custom shadow-none',
                'maxlength': '240',
                'aria-label': 'Comment text',
            }),
        }
