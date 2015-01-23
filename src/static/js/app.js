// Count all features included in the test page.
$('.feature-list').append(
  '<section class="feature-list_item block block__padded-top block__border-top">' +
  '<h1>jQuery</h1>' +
  '<p>jQuery is working and counts a total of ' +
  '<strong>' + $('.feature-list_item').size() + '</strong> ' +
  'cf-components.</p>' +
  '</section>'
);

// get data for each select input
// call the corresponding mustache template and fill the input
// set the first option as selected
function getUIData() {
	'use strict';
  $('select').each(function() {
    console.log('this is value = ' + this.id);
    var selectID = this.id;
    $.get(selectID + '.json', function(data) {
      console.log('this is value = ' + selectID);
      $.get('/hmda-viz-prototype/templates/' + selectID + '.html', function(templates) {
        var template = $(templates).filter('#' + selectID).html();
        var html = Mustache.to_html(template, data);
        console.log('html element = #' + selectID);
        $('#' + selectID).html(html);
        $('#' + selectID + ' option:first').attr('selected', 'selected');
      });
    });
  });
}

function getTableData(table) {
	'use strict';
  console.log('getting table ' + table);
  $.get(table + '.json', function(data) {
    $.get('/hmda-viz-prototype/templates/' + table + '.html', function(templates) {
      var template = $(templates).filter('#' + table).html();
      var html = Mustache.to_html(template, data);
      console.log('html element = #' + table);
      $('#' + table).html(html);
    });
  });
}

// update the button link
function setLink() {
	'use strict';
  //var newURL = '';  // needed on first page, year and state make the url
  $('select').each(function() {
    console.log ('select id = ' + $(this).val());
    newURL += $(this).val().replace(' ', '-').toLowerCase() + '/';
  });
  $('.js-btn').attr('href', newURL);
}

$( document ).ready(function() {
	'use strict';
  jQuery.ajaxSetup({async:false});  // no async!

  var urlPath = window.location.pathname.split('/');
  var path = urlPath[urlPath.length-2];

  if (urlPath.length === 8) {
    getTableData(path);
  } else {
    // fill the select inputs
    getUIData();
    // initial set link
    setLink();
    // call setlink when new choice is made
    $('select').click(function() {
      setLink();
    });
  }
});