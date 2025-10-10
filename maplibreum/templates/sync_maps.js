var primaryContainer = document.getElementById('{{ primary_map_id }}');
if (!primaryContainer) { return; }

var wrapper = document.createElement('div');
wrapper.className = 'maplibreum-sync-wrapper';
primaryContainer.parentNode.insertBefore(wrapper, primaryContainer);
wrapper.appendChild(primaryContainer);
primaryContainer.classList.add('maplibreum-sync-map');

var mapIds = ['{{ primary_map_id }}'];
var secondaryMaps = [];

{% for config in secondary_map_configs %}
var div = document.createElement('div');
div.id = '{{ config.container }}';
div.className = 'maplibreum-sync-map';
wrapper.appendChild(div);
mapIds.push('{{ config.container }}');

var secondaryMap = new maplibregl.Map({
    container: '{{ config.container }}',
    style: '{{ config.style }}',
    center: [{{ config.center[0] }}, {{ config.center[1] }}],
    zoom: {{ config.zoom }},
    maplibreLogo: true
});
secondaryMaps.push(secondaryMap);
{% endfor %}

var allMaps = [map].concat(secondaryMaps);

if (typeof syncMaps === 'function') {
    syncMaps.apply(null, allMaps);
}

window._maplibreumSyncedMaps = allMaps;
window._maplibreumSyncedCenter = map.getCenter();

function updateCenter(sourceMap) {
    window._maplibreumSyncedCenter = sourceMap.getCenter();
}

allMaps.forEach(function(m) {
    m.on('move', function() { updateCenter(m); });
});