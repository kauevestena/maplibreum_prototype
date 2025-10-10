# Next Steps for JavaScript Injection Reduction - October 9, 2025

## 🎯 Current Status

After completing the tracking audit (see [PROGRESS_REPORT_2025_10_09_TRACKING_AUDIT.md](PROGRESS_REPORT_2025_10_09_TRACKING_AUDIT.md)), the roadmap is now accurate:

- **Overall Progress**: 61.0% (75/123 examples)
- **Phase 1**: 48.0% (12/25 examples)
- **Phase 2**: 88.9% (8/9 examples, 1 remaining)
- **Phase 3**: 0% (0/22 examples)

## 🚀 Recommended Path Forward

### Priority 1: Complete Phase 2 (88.9% → 100%)

**Target Example**: `add-a-custom-layer-with-tiles-to-a-globe`

**Why This Matters:**
- Achieves 100% Phase 2 completion (major milestone)
- Demonstrates advanced WebGL/custom layer capabilities
- Sets strong precedent for handling complex rendering APIs
- Completes the "Enhanced Features" phase entirely

**Implementation Requirements:**
1. **CustomGlobeLayer API**: Python wrapper for WebGL tile rendering on globe projection
2. **GlobeTileRenderer**: Helper for managing shaders, meshes, and tile generation
3. **Shader Management**: Python-friendly interface for vertex/fragment shader configuration

**Estimated Effort**: Medium-High (2-4 hours)
- Complex WebGL code needs careful abstraction
- Shader management requires thoughtful API design
- Tile mesh generation logic needs Python interface

**Test File**: `tests/test_examples/test_add_a_custom_layer_with_tiles_to_a_globe.py`

**Current Implementation**: Uses `CustomLayer` with raw JavaScript for `on_add` and `render` methods

**Improvement Goal**: Create Python API that generates the shader and rendering logic

---

### Priority 2: Continue Phase 1 Medium-Priority Examples

After completing Phase 2, focus on medium-priority Phase 1 examples:

#### Quick Win Examples (Lower Complexity)

**A. view-local-geojson-experimental**
- Priority: Low
- Effort: Low
- Can leverage existing `GeoJSONSource.from_file()` API
- Minor enhancements for experimental features

**B. zoom-and-planet-size-relation-on-globe**
- Priority: Low
- Effort: Low-Medium
- Requires `GlobeInteraction` and `ZoomHandler` APIs
- Educational/demonstration example

#### Medium Complexity Examples (External Dependencies)

**C. sync-movement-of-multiple-maps**
- Priority: Medium
- Effort: Medium
- Requires: `MapSynchronizer`, `MultiMapContainer` APIs
- Niche but useful feature
- Currently uses external `@mapbox/mapbox-gl-sync-move` library

**D. geocode-with-nominatim**
- Priority: Medium
- Effort: Medium
- Requires: `GeocodingService`, `NominatimGeocoder` APIs
- Currently uses `@maplibre/maplibre-gl-geocoder` library
- Common use case, high value

**E. pmtiles-source-and-protocol**
- Priority: Medium
- Effort: Medium-High
- Requires: `PMTilesProtocol`, `PMTilesSource` APIs
- Modern tile format, growing adoption
- Protocol extension implementation

---

### Priority 3: Begin Phase 3 Planning

Phase 3 focuses on external library integration (22 examples):

#### Three.js Integration (4 examples)
- add-a-3d-model-using-threejs
- add-a-3d-model-to-globe-using-threejs
- adding-3d-models-using-threejs-on-terrain
- Requires: `ThreeJSLayer`, `Model3D` APIs

#### Deck.GL Integration (2 examples)
- create-deckgl-layer-using-rest-api
- toggle-deckgl-layer
- Requires: `DeckGLLayer`, `RESTDataSource` APIs

#### Drawing Tools Integration (2 examples)
- draw-geometries-with-terra-draw
- draw-polygon-with-mapbox-gl-draw
- Requires: `TerraDrawWrapper`, `MapboxDrawWrapper` APIs

#### Other Advanced Features (14 examples)
- Various protocol extensions, custom integrations

**Phase 3 Strategy:**
1. Design consistent wrapper pattern for external libraries
2. Implement one example from each category as proof-of-concept
3. Standardize API patterns across similar integrations
4. Document best practices for library wrappers

---

## 📊 Impact Analysis

### Completing Phase 2 (Option A)
- **Progress Impact**: +0.8% (61.0% → 61.8%)
- **Phase Completion**: Phase 2 reaches 100% ✅
- **Milestone Value**: High (complete phase milestone)
- **Technical Value**: High (demonstrates advanced capabilities)
- **User Value**: Medium (niche use case)

### Continuing Phase 1 (Option B)
- **Progress Impact**: +0.8% per example (up to +10.4% for all 13 remaining)
- **Phase Completion**: Phase 1 could reach 100% ✅
- **Milestone Value**: Very High (complete core API phase)
- **Technical Value**: Medium-High (core functionality)
- **User Value**: High (common use cases)

### Beginning Phase 3 (Option C)
- **Progress Impact**: +0.8% per example (up to +17.9% for all 22)
- **Phase Completion**: Phase 3 begins progress
- **Milestone Value**: Medium (starting new phase)
- **Technical Value**: Medium (advanced features)
- **User Value**: Medium (specialized use cases)

---

## 🎯 Recommended Action Plan

### Week 1: Complete Phase 2
1. Implement `CustomGlobeLayer` and `GlobeTileRenderer` APIs
2. Convert `add-a-custom-layer-with-tiles-to-a-globe` example
3. Test and document the new APIs
4. **Milestone**: 🎉 Phase 2 100% Complete!

### Week 2-3: Phase 1 Quick Wins
5. Convert `view-local-geojson-experimental` (leverage existing API)
6. Convert `zoom-and-planet-size-relation-on-globe` (globe interactions)
7. Convert `geocode-with-nominatim` (high-value feature)
8. Convert `sync-movement-of-multiple-maps` (useful feature)

### Week 4+: Phase 1 Medium Priority
9. Convert `pmtiles-source-and-protocol` (modern tile format)
10. Design drawing tools wrapper strategy
11. Implement one drawing tool example as proof-of-concept

### Long-term: Phase 3 Strategy
12. Design external library wrapper pattern
13. Implement Three.js integration examples
14. Implement Deck.GL integration examples
15. Complete drawing tools integration
16. **Milestone**: 🎉 All Phases Complete!

---

## 📈 Success Metrics

### Short-term Goals (Next 2 Weeks)
- ✅ Phase 2: 100% complete (1 example remaining)
- ✅ Phase 1: 56%+ complete (14+ examples, +2 examples)
- ✅ Overall: 63%+ complete (77+ examples)

### Medium-term Goals (Next Month)
- ✅ Phase 1: 72%+ complete (18+ examples, +6 examples)
- ✅ Overall: 66%+ complete (81+ examples)
- ✅ Begin Phase 3 planning and proof-of-concept

### Long-term Goals (3 Months)
- ✅ Phase 1: 100% complete (25 examples)
- ✅ Phase 2: 100% complete (9 examples)
- ✅ Phase 3: 40%+ complete (9+ examples)
- ✅ Overall: 80%+ complete (98+ examples)

---

## 🎓 Implementation Guidelines

### API Design Principles
1. **Pythonic Interface**: APIs should feel natural in Python
2. **Type Safety**: Use type hints and dataclasses
3. **Composability**: APIs should work well together
4. **Testability**: Easy to unit test without browser
5. **Documentation**: Clear examples and docstrings

### Testing Standards
1. **Unit Tests**: Test Python API logic
2. **Integration Tests**: Test generated JavaScript
3. **HTML Validation**: Verify rendered output
4. **Backward Compatibility**: Don't break existing tests

### Documentation Standards
1. **Progress Reports**: One per major session
2. **API Documentation**: Update after each new API
3. **Roadmap Updates**: Keep JSON and markdown in sync
4. **Example Notebooks**: Demonstrate new APIs

---

## 📝 Conclusion

The JavaScript injection reduction effort is progressing well at 61.0% completion. The immediate recommendation is to **complete Phase 2** by implementing the final custom layer example, achieving a 100% Phase 2 milestone. This would demonstrate advanced API capabilities and set a strong foundation for continuing Phase 1 work.

After Phase 2 completion, focus should shift to medium-priority Phase 1 examples, prioritizing common use cases like geocoding and modern features like PMTiles support. Phase 3 planning can begin once Phase 1 reaches 70%+ completion.

---

**Document Date**: October 9, 2025  
**Status**: Active Roadmap  
**Next Review**: After Phase 2 completion  
**Roadmap Version**: v3.1.0
