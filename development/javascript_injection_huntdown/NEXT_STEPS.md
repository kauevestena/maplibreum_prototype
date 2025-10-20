# Next Steps for JavaScript Injection Reduction - October 14, 2025

## 🎯 Current Status

After completing the tracking audit (see [PROGRESS_REPORT_2025_10_09_TRACKING_AUDIT.md](PROGRESS_REPORT_2025_10_09_TRACKING_AUDIT.md)), the roadmap is now accurate:

- **Overall Progress**: 69.1% (85/123 examples)
- **Phase 1**: 48.0% (12/25 examples)
- **Phase 2**: 100% (15/15 examples)
- **Phase 3**: 13.6% (3/22 examples)

## 🚀 Recommended Path Forward

### Priority 1: Ship Protocol & Deck.GL Conversions (high-impact backlog)

**Target Examples**:
- `pmtiles-source-and-protocol`
- `toggle-deckgl-layer`
- `use-addprotocol-to-transform-feature-properties`

**Why This Matters:**
- Unlocks modern PMTiles delivery and protocol extension stories demanded by data-heavy workflows
- Demonstrates that the new `DeckGLLayer` stack can support dynamic toggling without manual JavaScript
- Establishes a reusable protocol-extension interface that Phase 3 examples can build upon
- Raises overall completion by ~2.4 percentage points once all three land

**Implementation Requirements:**
1. **PMTilesProtocol / PMTilesSource**: register PMTiles handlers from Python and expose friendly configuration hooks
2. **DeckGLLayer.toggle() support**: expose deck.gl layer lifecycle controls and pair them with a `LayerToggleControl`
3. **ProtocolExtension & FeatureTransformer APIs**: surface `map.addProtocol()` equivalents with validation and transform callbacks

**Estimated Effort**: Medium-High (collectively 6-9 engineering days)
- Protocol registration requires async-safe resource loading and cache management
- Deck.GL toggling must coordinate with existing layer management abstractions
- Protocol extensions need guardrails to prevent unsafe JavaScript execution

**Test Files**:
- `tests/test_examples/test_pmtiles_source_and_protocol.py`
- `tests/test_examples/test_toggle_deckgl_layer.py`
- `tests/test_examples/test_use_addprotocol_to_transform_feature_properties.py`

**Current Implementation**: Direct JavaScript hooks (`map.addProtocol`, manual Deck.GL toggles) executed through `add_on_load_js()` with no Python visibility.

**Improvement Goal**: Provide first-class Python APIs for registering protocols, wiring deck.gl toggles, and applying feature transforms so notebooks never need custom injection for these workflows.

---

### Priority 2: Complete Drawing Tool Wrappers

**Target Examples**:
- `draw-geometries-with-terra-draw`
- `draw-polygon-with-mapbox-gl-draw`

**Why This Matters:**
- Finishes the outstanding third-party drawing integrations in Phase 3
- Establishes a common drawing-tool abstraction that subsequent geospatial editing features can reuse
- Eliminates the final external-library dependencies that still require raw script tags

**Implementation Requirements:**
1. **TerraDrawWrapper**: manage lifecycle, mode switching, and event callbacks for Terra Draw
2. **MapboxDrawWrapper / PolygonDrawTool**: expose shape editing, styling, and export helpers for Mapbox GL Draw
3. Shared **DrawingTools** base class: unify enable/disable semantics and event propagation

**Estimated Effort**: Medium (4-6 engineering days combined)
- Both libraries require bundling assets and mapping their event systems into Python callbacks
- Need robust serialization helpers so tests can assert drawn geometry without browser interaction

**Test Files**:
- `tests/test_examples/test_draw_geometries_with_terra_draw.py`
- `tests/test_examples/test_draw_polygon_with_mapbox_gl_draw.py`

**Current Implementation**: Adds external scripts and inline JavaScript to register drawing tools and emit geometry events.

**Improvement Goal**: Deliver Python-native drawing APIs that configure the tools, surface draw events, and serialize results directly to notebook outputs.

---

### Priority 3: Raise Phase 1 Completion (13 examples remaining)

Phase 1 still has 13 JavaScript-injection-first demos that rely on `add_on_load_js()` for navigation, pointer inspection, or bespoke UI toggles.

**Focus Areas:**
- Harden the navigation utilities (`Map.fly_to`, `Map.ease_to`, sequencing helpers) so every tutorial-level map interaction is injection-free
- Standardize pointer feedback patterns (hover tooltips, feature-inspection popups) with reusable event handlers
- Provide lightweight control factories for any lingering checkbox/button demos that still wire DOM listeners manually

**Why This Matters:**
- Completing the core API phase pushes overall proper-API usage toward the 80% goal faster than advanced integrations alone
- Reduces onboarding friction for new users who primarily copy Phase 1 examples
- Ensures the infrastructure built for Phase 2 can be consumed consistently across entry-level demos

**Implementation Approach:**
1. Audit the remaining Phase 1 tests to catalog the specific interaction gaps
2. Apply existing control/event abstractions before introducing new APIs
3. Reserve new helper implementations for behaviors that appear in multiple remaining examples

---

## 📊 Impact Analysis

### Option A: Deliver protocol & Deck.GL conversions (Priority 1)
- **Progress Impact**: ~+2.4% (69.1% → ~71.5%) from three example upgrades
- **Phase Completion**: Phase 3 jumps from 13.6% (3/22) → 27.3% (6/22)
- **Milestone Value**: High — completes all protocol-centric backlog items
- **Technical Value**: High — exercises new data pipeline abstractions and deck.gl lifecycle management
- **User Value**: High — unblocks common "bring your own tiles" and deck.gl toggling workflows

### Option B: Finish drawing wrappers (Priority 2)
- **Progress Impact**: ~+1.6% (two examples)
- **Phase Completion**: Phase 3 would reach 22.7% (5/22) if done before Option A, or 36.4% (8/22) after it
- **Milestone Value**: Medium-High — closes remaining third-party integration category
- **Technical Value**: Medium — focuses on lifecycle wiring and event plumbing
- **User Value**: Medium-High — interactive editing is a visible differentiator in demos

### Option C: Accelerate Phase 1 conversions (Priority 3)
- **Progress Impact**: ~+0.8% per example (e.g., +3.2% for four conversions)
- **Phase Completion**: 48.0% → 64.0% (12/25 → 16/25) with four quick wins
- **Milestone Value**: High — puts the foundational API phase within striking distance of 80%
- **Technical Value**: Medium — leans on existing controls/events with limited new infrastructure
- **User Value**: High — these examples represent the most-used getting-started workflows

---

## 🎯 Recommended Action Plan

### Week 1-2: Protocol & Deck.GL backlog
1. Implement `PMTilesProtocol`/`PMTilesSource` with caching + credential support
2. Add Deck.GL layer toggle support (Python lifecycle + control wiring)
3. Introduce protocol-extension helpers for feature transformers
4. Ship updated tests + docs for all three examples

### Week 3: Drawing tool wrappers
5. Build `TerraDrawWrapper` + shared drawing base class
6. Implement `MapboxDrawWrapper`/`PolygonDrawTool`
7. Document drawing APIs and finalize the two remaining examples

### Week 4+: Phase 1 acceleration
8. Audit remaining Phase 1 examples for reusable patterns
9. Convert 3-4 quick wins using existing controls/events each sprint
10. Track incremental progress toward 80% proper API usage goal

### Long-term: Phase 3 depth
11. Generalize protocol/drawing patterns to other external integrations
12. Expand test coverage for advanced data streams and multi-layer synchronization
13. **Milestone**: 🎉 Phase 3 ≥40% complete and Phase 1 ≥80% complete

---

## 📈 Success Metrics

### Short-term Goals (Next 2 Weeks)
- ✅ Protocol & Deck.GL conversions merged (Phase 3 ≥27.3%, 6/22)
- ✅ Overall progress ≥71.5% (88/123 examples)
- ✅ New PMTiles/Deck.GL/protocol APIs documented and tested

### Medium-term Goals (Next Month)
- ✅ Drawing wrappers delivered (Phase 3 ≥36.4%, 8/22)
- ✅ Phase 1 ≥56% complete (14/25 examples) through quick-win conversions
- ✅ Overall progress ≥73.5% (90/123 examples)

### Long-term Goals (3 Months)
- ✅ Phase 1 ≥80% complete (20/25 examples)
- ✅ Phase 3 ≥45% complete (10/22 examples)
- ✅ Overall progress ≥78% (96/123 examples)
- ✅ External-integration APIs share consistent lifecycle + testing patterns

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

With Phase 2 now fully complete and overall progress at 69.1%, the roadmap turns to the remaining high-impact injection hotspots. The immediate priority is to **replace the protocol and deck.gl JavaScript shims with native Python APIs**, raising Phase 3 coverage to 27.3% and unlocking PMTiles, deck.gl toggling, and custom protocol workflows for users.

Once those integrations land, finish the drawing-tool wrappers and reinvest momentum into the 13 outstanding Phase 1 demos. This cadence keeps the spotlight on visible wins while steadily marching toward the 80% proper-API usage objective and, ultimately, a zero-injection example gallery.

---

**Document Date**: October 14, 2025
**Status**: Active Roadmap
**Next Review**: After protocol & Deck.GL conversions land
**Roadmap Version**: v3.8.0
