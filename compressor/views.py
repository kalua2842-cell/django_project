import os
import io
import uuid
from django.shortcuts import render
from django.conf import settings
from PIL import Image, ImageFile
from .forms import ImageProcessForm

ImageFile.LOAD_TRUNCATED_IMAGES = True

def upload_view(request):
    if request.method == 'POST':
        form = ImageProcessForm(request.POST, request.FILES)
        if form.is_valid():
            imgfile = request.FILES['image']
            target_format = form.cleaned_data['target_format']
            compress_level = form.cleaned_data.get('compress_level') or 6
            webp_lossless = form.cleaned_data.get('webp_lossless')
            jpeg_quality = form.cleaned_data.get('jpeg_quality') or 85

            img = Image.open(imgfile)
            img = img.convert('RGBA') if img.mode == 'P' else img

            orig_format = img.format or os.path.splitext(imgfile.name)[1].replace('.', '').upper()
            out_format = target_format.upper() if target_format != 'keep' else orig_format

            out_ext = 'jpg' if out_format == 'JPEG' else out_format.lower()
            out_name = f"{uuid.uuid4().hex}.{out_ext}"
            out_path = os.path.join(settings.MEDIA_ROOT, out_name)
            os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

            save_kwargs = {}
            if out_format == 'PNG':
                save_kwargs['optimize'] = True
                save_kwargs['compress_level'] = compress_level
            elif out_format == 'WEBP':
                if webp_lossless:
                    save_kwargs['lossless'] = True
                else:
                    save_kwargs['quality'] = jpeg_quality
            elif out_format == 'JPEG':
                if img.mode in ('RGBA', 'LA'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[3])
                    img = background
                else:
                    img = img.convert('RGB')
                save_kwargs['quality'] = jpeg_quality
                save_kwargs['optimize'] = True

            bio = io.BytesIO()
            try:
                img.save(bio, format=out_format, **save_kwargs)
            except Exception:
                bio = io.BytesIO()
                img.save(bio, format='PNG', optimize=True, compress_level=compress_level)
                out_name = f"{uuid.uuid4().hex}.png"
                out_path = os.path.join(settings.MEDIA_ROOT, out_name)

            with open(out_path, 'wb') as f:
                f.write(bio.getvalue())

            result_url = settings.MEDIA_URL + out_name
            context = {
                'result_url': result_url,
                'result_filename': out_name,
                'orig_name': imgfile.name,
                'orig_format': orig_format,
                'out_format': out_format,
                'out_size': os.path.getsize(out_path),
            }
            return render(request, 'compressor/result.html', context)
    else:
        form = ImageProcessForm()
    return render(request, 'compressor/upload.html', {'form': form})



