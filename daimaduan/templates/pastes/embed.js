{% for code in paste.codes -%}
document.write('<pre><code>{{ code.content | e | replace('\n', '\\n') | replace('\r', '') }}</code></pre>');
{% endfor -%}