---
privatus_props:
  nasty: "</script><script>window.__pwned=1</script>  &<>\"'"
---
# Nasty

The page props above go through the plugin. MkDocs has no event helper, so the
button's attribute is written in the page with HTML entities.

<button type="button" data-privatus-event="Nasty value" data-privatus-prop-nasty="&lt;/script&gt;&lt;script&gt;window.__pwned=1&lt;/script&gt;&#x2028;&#x2029;&amp;&lt;&gt;&quot;&#39;">Nasty</button>
