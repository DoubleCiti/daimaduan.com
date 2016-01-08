document.write('<link rel="stylesheet" href="http://{{ config['site.domain'] }}/static/css/embed.css" />');
{% for code in paste.codes -%}
document.write('<div class="daimaduan-code" id="paste-{{ paste.hash_id }}">');
document.write('<div class="daimaduan-code-block">');
document.write('{{ code.highlight_content | replace('\n', '\\n') | replace('\r', '') | safe }}');
document.write('</div><div class="daimaduan-code-meta"><a href="http://{{ config['site.domain'] }}" style="float: right">代码段</a><a href="http://{{ config['site.domain'] }}/paste/{{ paste.hash_id }}#code-{{ code.hash_id }}">{{ code.title }}</a></div></div>');
{% endfor -%}