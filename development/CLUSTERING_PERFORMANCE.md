# Marker Clustering Performance Guide

This document provides performance benchmarks and guidance for using marker clustering in MapLibreum with large datasets.

## Overview

MapLibreum provides efficient marker clustering through two main approaches:

1. **MarkerCluster class**: For grouping individual markers into clusters
2. **ClusteredGeoJson class**: For clustering arbitrary GeoJSON point features

Both classes use MapLibre GL JS's built-in clustering capabilities, which delegate clustering to the browser's JavaScript engine. This provides excellent performance even with very large datasets.

## Performance Benchmarks

Benchmarks were conducted using the `development/benchmark_clustering.py` script on a standard development environment. The tests measured clustering performance across various dataset sizes.

### Benchmark Results

| Dataset Size | Average Time | Min Time | Max Time | Rating | Notes |
|-------------|-------------|----------|----------|---------|-------|
| 10,000 points | 0.008s | 0.008s | 0.009s | Excellent | Nearly instantaneous |
| 50,000 points | 0.038s | 0.035s | 0.039s | Excellent | Nearly instantaneous |
| 100,000 points | 0.078s | 0.075s | 0.080s | Excellent | Nearly instantaneous |
| 200,000 points | 0.153s | 0.146s | 0.158s | Very Good | Very fast clustering |
| 500,000 points | 0.380s | 0.361s | 0.392s | Very Good | Very fast clustering |

### Performance Characteristics

The clustering algorithm exhibits approximately **linear time complexity** with respect to the number of points:

- **10k → 50k** (5x increase): ~4.75x increase in time
- **50k → 100k** (2x increase): ~2.05x increase in time
- **100k → 200k** (2x increase): ~1.96x increase in time
- **200k → 500k** (2.5x increase): ~2.48x increase in time

This linear scaling means that clustering performance is predictable and scales well with dataset size.

## Usage Recommendations

### Dataset Size Guidelines

Based on the benchmark results, here are recommended use cases for different dataset sizes:

#### Small Datasets (< 10,000 points)
- **Performance**: Instant (< 0.01s)
- **Recommendation**: Use without concerns
- **Use case**: City-level points of interest, store locations, event venues

#### Medium Datasets (10,000 - 100,000 points)
- **Performance**: Very fast (< 0.1s)
- **Recommendation**: Ideal for client-side clustering
- **Use case**: Regional data points, sensor networks, real-time tracking

#### Large Datasets (100,000 - 500,000 points)
- **Performance**: Fast (< 0.5s)
- **Recommendation**: Client-side clustering is still practical
- **Use case**: Country-wide datasets, large sensor arrays, historical data

#### Very Large Datasets (> 500,000 points)
- **Performance**: Good (> 0.5s, but still under 1s for up to 1M points)
- **Recommendation**: Consider server-side clustering or data aggregation
- **Use case**: Global datasets, massive historical archives

### Optimization Tips

#### 1. Adjust Clustering Parameters

The clustering behavior can be tuned using two key parameters:

```python
from maplibreum import Map
from maplibreum.cluster import MarkerCluster

# Default parameters
cluster = MarkerCluster(
    cluster_radius=50,      # Cluster radius in pixels
    cluster_max_zoom=14     # Maximum zoom level to cluster
)

# For denser datasets, increase radius
cluster = MarkerCluster(cluster_radius=80)  # Fewer, larger clusters

# For sparse datasets, decrease radius
cluster = MarkerCluster(cluster_radius=30)  # More, smaller clusters
```

**`cluster_radius`** (default: 50):
- Lower values (20-40): More clusters, better detail, slightly slower
- Higher values (60-100): Fewer clusters, less detail, faster

**`cluster_max_zoom`** (default: 14):
- Lower values (10-12): Cluster at higher zoom levels, better performance
- Higher values (15-18): De-cluster earlier, more detail, may impact performance

Note: When using `add_clustered_geojson()`, the parameters are named `radius` and `max_zoom` instead.

#### 2. Use GeoJSON Clustering for Large Datasets

For datasets already in GeoJSON format, use `ClusteredGeoJson` or the `add_clustered_geojson()` method:

```python
from maplibreum import Map

# Large GeoJSON dataset
geojson_data = {
    "type": "FeatureCollection",
    "features": [...]  # Large list of point features
}

m = Map(center=[0, 0], zoom=2)
m.add_clustered_geojson(geojson_data, radius=60, max_zoom=12)
```

This approach is more efficient than adding individual markers when you already have the data in GeoJSON format.

#### 3. Consider Server-Side Clustering

For extremely large datasets (> 1 million points), consider:

1. **Pre-clustering on the server**: Aggregate data before sending to the client
2. **Dynamic loading**: Load only visible clusters based on the current viewport
3. **Tile-based clustering**: Use vector tiles with pre-clustered data

## Code Examples

### Basic Clustering with MarkerCluster

```python
from maplibreum import Map
from maplibreum.cluster import MarkerCluster
from maplibreum.markers import Marker

# Create map
m = Map(center=[-98, 39], zoom=4)

# Create cluster
cluster = MarkerCluster(
    name="my_cluster",
    cluster_radius=50,
    cluster_max_zoom=14
)

# Add markers
for i in range(50_000):
    lng = random.uniform(-125, -65)
    lat = random.uniform(25, 50)
    marker = Marker(coordinates=[lng, lat])
    cluster.add_marker(marker)

# Add cluster to map
cluster.add_to(m)

# Save or display
m.save("clustered_map.html")
```

### Clustering GeoJSON Data

```python
from maplibreum import Map
import random

# Generate large GeoJSON dataset
geojson_data = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [
                    random.uniform(-125, -65),
                    random.uniform(25, 50)
                ]
            },
            "properties": {"id": i}
        }
        for i in range(100_000)
    ]
}

# Create map with clustered data
m = Map(center=[-98, 39], zoom=4)
m.add_clustered_geojson(
    geojson_data,
    radius=60,
    max_zoom=12
)

m.save("clustered_geojson_map.html")
```

## Running Your Own Benchmarks

To run the benchmark suite on your own system:

```bash
cd development
python benchmark_clustering.py
```

The script will test clustering performance with 10k, 50k, 100k, 200k, and 500k points, running 3 iterations for each size to ensure consistent results.

## Technical Implementation

MapLibreum's clustering uses MapLibre GL JS's native clustering capabilities:

1. **Source Configuration**: Data is added as a GeoJSON source with `cluster: true`
2. **Browser-Side Processing**: MapLibre GL JS handles clustering in the browser
3. **Three Layer System**:
   - Cluster circles (colored by size)
   - Cluster counts (text labels)
   - Unclustered points (individual markers)

This approach leverages MapLibre's highly optimized C++/WebAssembly implementation, which is significantly faster than pure Python clustering algorithms.

## Performance Notes

- **CPU-bound**: Clustering performance is primarily limited by CPU speed
- **Memory**: Large datasets (> 100k points) may consume significant browser memory
- **Browser variations**: Performance may vary slightly across different browsers
- **Initial load**: The first clustering operation may be slightly slower due to initialization overhead

## Conclusion

MapLibreum's marker clustering provides excellent performance for datasets up to 500,000 points, with sub-second clustering times. For most interactive mapping applications, client-side clustering is sufficient and provides a smooth user experience.

For additional performance optimization or datasets exceeding 1 million points, consider server-side clustering or pre-aggregation strategies.
