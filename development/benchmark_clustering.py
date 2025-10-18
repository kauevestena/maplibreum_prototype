#!/usr/bin/env python3
"""Benchmark marker clustering performance on large datasets.

This script benchmarks the clustering performance of MapLibreum with various
dataset sizes to provide guidance on expected performance characteristics.
"""

import random
import time
import sys
from pathlib import Path

# Add parent directory to path to import maplibreum
sys.path.insert(0, str(Path(__file__).parent.parent))

from maplibreum.cluster import cluster_features


def generate_random_features(count):
    """Generate random GeoJSON point features.
    
    Parameters
    ----------
    count : int
        Number of features to generate.
        
    Returns
    -------
    list
        List of GeoJSON feature objects.
    """
    return [
        {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [
                    random.uniform(-180, 180),
                    random.uniform(-90, 90),
                ],
            },
            "properties": {"id": i},
        }
        for i in range(count)
    ]


def benchmark_clustering(point_counts, radius=40, max_zoom=16, iterations=3):
    """Benchmark clustering performance for different dataset sizes.
    
    Parameters
    ----------
    point_counts : list of int
        List of point counts to benchmark.
    radius : int, optional
        Cluster radius in pixels (default: 40).
    max_zoom : int, optional
        Maximum zoom level for clustering (default: 16).
    iterations : int, optional
        Number of iterations to run for each point count (default: 3).
        
    Returns
    -------
    dict
        Dictionary mapping point counts to timing results.
    """
    results = {}
    
    for count in point_counts:
        print(f"\nBenchmarking {count:,} points...")
        timings = []
        
        for i in range(iterations):
            print(f"  Iteration {i + 1}/{iterations}...", end=" ", flush=True)
            
            # Generate features
            features = generate_random_features(count)
            
            # Time the clustering operation
            start = time.perf_counter()
            index = cluster_features(features, radius=radius, max_zoom=max_zoom)
            
            # Get clusters at world view (zoom 0)
            clusters = index.get_clusters([-180, -90, 180, 90], 0)
            
            duration = time.perf_counter() - start
            timings.append(duration)
            print(f"{duration:.3f}s ({len(clusters)} clusters)")
        
        avg_time = sum(timings) / len(timings)
        min_time = min(timings)
        max_time = max(timings)
        
        results[count] = {
            "average": avg_time,
            "min": min_time,
            "max": max_time,
            "timings": timings,
        }
        
        print(f"  Average: {avg_time:.3f}s (min: {min_time:.3f}s, max: {max_time:.3f}s)")
    
    return results


def print_summary(results):
    """Print a summary of benchmark results.
    
    Parameters
    ----------
    results : dict
        Dictionary of benchmark results from benchmark_clustering().
    """
    print("\n" + "=" * 70)
    print("BENCHMARK SUMMARY")
    print("=" * 70)
    print(f"{'Points':>10} | {'Avg Time':>10} | {'Min Time':>10} | {'Max Time':>10}")
    print("-" * 70)
    
    for count, data in sorted(results.items()):
        print(
            f"{count:>10,} | {data['average']:>8.3f}s | {data['min']:>8.3f}s | {data['max']:>8.3f}s"
        )
    
    print("=" * 70)


def print_guidance(results):
    """Print performance guidance based on benchmark results.
    
    Parameters
    ----------
    results : dict
        Dictionary of benchmark results from benchmark_clustering().
    """
    print("\n" + "=" * 70)
    print("PERFORMANCE GUIDANCE")
    print("=" * 70)
    
    for count, data in sorted(results.items()):
        avg_time = data["average"]
        
        if avg_time < 0.1:
            rating = "Excellent"
            description = "Clustering is nearly instantaneous"
        elif avg_time < 0.5:
            rating = "Very Good"
            description = "Clustering is very fast"
        elif avg_time < 1.0:
            rating = "Good"
            description = "Clustering is fast enough for interactive use"
        elif avg_time < 2.0:
            rating = "Acceptable"
            description = "Clustering may cause slight delays"
        elif avg_time < 5.0:
            rating = "Marginal"
            description = "Clustering may cause noticeable delays"
        else:
            rating = "Poor"
            description = "Clustering will cause significant delays"
        
        print(f"\n{count:,} points:")
        print(f"  Rating: {rating}")
        print(f"  Average time: {avg_time:.3f}s")
        print(f"  {description}")
    
    print("\n" + "=" * 70)
    print("\nRECOMMENDATIONS:")
    print("-" * 70)
    print("• For interactive maps, aim to keep clustering time under 1 second")
    print("• Consider server-side clustering for datasets over 100k points")
    print("• Adjust cluster_radius and cluster_max_zoom to optimize performance")
    print("• Use MapLibre's built-in clustering (as done by MarkerCluster)")
    print("  for best performance on large datasets")
    print("=" * 70 + "\n")


def main():
    """Run the benchmarking suite."""
    print("MapLibreum Clustering Performance Benchmark")
    print("=" * 70)
    print("This benchmark measures clustering performance across various")
    print("dataset sizes to provide guidance on expected performance.")
    print("=" * 70)
    
    # Define dataset sizes to benchmark
    point_counts = [10_000, 50_000, 100_000, 200_000, 500_000]
    
    # Run benchmarks
    results = benchmark_clustering(point_counts, iterations=3)
    
    # Print results
    print_summary(results)
    print_guidance(results)


if __name__ == "__main__":
    main()
