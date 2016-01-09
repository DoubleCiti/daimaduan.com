{% set root_url = url_for() -%}
document.write('<link rel="stylesheet" href="{{ root_url }}/static/css/embed.css" />');
{% for code in paste.codes -%}
document.write('<div class="daimaduan-code" id="paste-{{ paste.hash_id }}">');
document.write('<div class="daimaduan-code-block">');
document.write('{{ code.highlight_content | replace('\n', '\\n') | replace('\r', '') | safe }}');
document.write('</div><div class="daimaduan-code-meta"><div class="daimaduan-copyright">powered by <a href="{{ root_url }}"><strong>代码段</strong></a></div><div class="daimaduan-code-name"><a href="{{ root_url }}/paste/{{ paste.hash_id }}#code-{{ code.hash_id }}">{{ code.title * 10 }}</a></div></div></div>');
{% endfor -%}