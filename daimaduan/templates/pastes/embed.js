document.write('<link rel="stylesheet" href="http://{{ config['site.domain'] }}/static/css/embed.css" />');
{% for code in paste.codes -%}
document.write('{{ code.highlight_content | replace('\n', '\\n') | replace('\r', '') | safe }}');
{% endfor -%}