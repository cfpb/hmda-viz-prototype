All notable changes to this project will be documented in this file.
We follow the [Semantic Versioning 2.0.0](http://semver.org/) format.


## 0.7.0 - 2015-01-16

### Changed
- Replaces all CFPB color variables with non-CFPB colors. To add the CFPB theme
  to your project you will need to include the CFPB color palette and the
  Capital Framework theme overrides file. Both files can be found in the
  generator-cf repo here:
  <https://github.com/cfpb/generator-cf/tree/master/app/templates/src/static/css>
  Background info on the new Capital Framework color variables can be found at
  <https://github.com/cfpb/capital-framework/issues/115>.

### Updated
- Dependencies.


## 0.6.2 - 2014-12-05

### Added
- Update cf-component-demo dev dependency to 0.9.0


## 0.6.1 - 2014-10-28

### Added
- Animated cues.


## 0.6.0 - 2014-10-28

### Added
- Infinite nesting.
- Programmatic access to expand and collapse functions.

### Fixed
- Toggle cues now work when outside of `.expandable_header`.


## 0.5.2 - 2014-10-08

### Fixed
- Improved focus states on `.expandable_target`.


## 0.5.1 - 2014-10-03

### Fixed
- Tweaked JS and CSS to correctly handle nested expandables.


## 0.5.0 - 2014-09-02

### Added
- Expandable group patterns, including an accordion-style option
  (only one open at a time)
- Tests for the new accordion-related JS
