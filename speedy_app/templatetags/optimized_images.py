from django import template
from django.templatetags.static import static
register = template.Library()

@register.simple_tag
def optimized_image(src_path, alt='', classes='', sizes=''):
    """Return a picture element with webp source and img fallback and a small srcset."""
    # src_path expected relative to static, e.g. 'images/servicios1.jpeg'
    base = static(src_path)
    webp = base.rsplit('.', 1)[0] + '.webp'
    # small srcset example (could be improved with real responsive images)
    srcset = f"{base} 1x, {base} 2x"
    sizes_attr = f' sizes="{sizes}"' if sizes else ''
    class_attr = f' class="{classes}"' if classes else ''
    html = f"""
    <picture>
      <source srcset="{webp}" type="image/webp">
      <img src="{base}" srcset="{srcset}" alt="{alt}"{class_attr}{sizes_attr} loading="lazy" decoding="async">
    </picture>
    """
    return html
