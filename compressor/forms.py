from django import forms

FORMAT_CHOICES = [
    ('keep', 'Keep original format'),
    ('PNG', 'PNG (lossless)'),
    ('WEBP', 'WebP (lossless possible)'),
    ('JPEG', 'JPEG (lossy)'),
]

class ImageProcessForm(forms.Form):
    image = forms.ImageField(required=True)
    target_format = forms.ChoiceField(choices=FORMAT_CHOICES, initial='keep')
    compress_level = forms.IntegerField(
        label='PNG compress level (0-9, 9 = max compression)',
        min_value=0, max_value=9, initial=6, required=False
    )
    webp_lossless = forms.BooleanField(label='Use lossless WebP (if available)', required=False)
    jpeg_quality = forms.IntegerField(label='JPEG quality (1-95)', min_value=1, max_value=95, initial=85, required=False)
